import csv, secrets, string
from io import StringIO
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.db.models import Sum, Count
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .forms import RegisterForm, RedeemForm
from .models import CustomerProfile, ProductCode, PointsTransaction, Reward, RewardClaim

def home(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return render(request, "home.html")

def register(request):
    if request.user.is_authenticated: return redirect("dashboard")
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        CustomerProfile.objects.get_or_create(user=user)
        login(request, user)
        messages.success(request, "Welcome to PerkBox. Your rewards wallet is ready.")
        return redirect("dashboard")
    return render(request, "registration/register.html", {"form": form})

@login_required
def dashboard(request):
    profile, _ = CustomerProfile.objects.get_or_create(user=request.user)
    txns = request.user.point_transactions.order_by("-created_at")[:6]
    claims = request.user.reward_claims.select_related("reward").order_by("-requested_at")[:4]
    return render(request, "dashboard.html", {"profile": profile, "transactions": txns, "claims": claims})

@login_required
def redeem_code(request):
    form = RedeemForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        code_value = form.cleaned_data["code"]
        try:
            with transaction.atomic():
                code = ProductCode.objects.select_for_update().get(code=code_value)
                if code.is_redeemed:
                    messages.error(request, "This product code has already been redeemed.")
                else:
                    updated = ProductCode.objects.filter(pk=code.pk, is_redeemed=False).update(
                        is_redeemed=True, redeemed_by=request.user, redeemed_at=timezone.now())
                    if updated != 1:
                        messages.error(request, "This code was just redeemed. Please try another code.")
                    else:
                        profile, _ = CustomerProfile.objects.get_or_create(user=request.user)
                        profile.points += code.points_value
                        profile.save(update_fields=["points"])
                        PointsTransaction.objects.create(user=request.user, amount=code.points_value,
                            transaction_type=PointsTransaction.EARN, description=f"Box code {code.code[-4:]} redeemed")
                        messages.success(request, f"Success! {code.points_value} points added to your wallet.")
        except ProductCode.DoesNotExist:
            messages.error(request, "We couldn't verify that code. Check the code inside your box and try again.")
        return redirect("redeem")
    return render(request, "redeem.html", {"form": form})

@login_required
def reward_catalogue(request):
    rewards = Reward.objects.filter(active=True, stock__gt=0).order_by("points_cost")
    profile, _ = CustomerProfile.objects.get_or_create(user=request.user)
    return render(request, "rewards.html", {"rewards": rewards, "profile": profile})

@login_required
def claim_reward(request, reward_id):
    if request.method != "POST": return redirect("reward_catalogue")
    with transaction.atomic():
        reward = Reward.objects.select_for_update().filter(pk=reward_id, active=True, stock__gt=0).first()
        profile = CustomerProfile.objects.select_for_update().get(user=request.user)
        if not reward:
            messages.error(request, "This reward is currently unavailable.")
        elif profile.points < reward.points_cost:
            messages.error(request, "You don't have enough points for this reward yet.")
        else:
            profile.points -= reward.points_cost
            profile.save(update_fields=["points"])
            claim = RewardClaim.objects.create(user=request.user, reward=reward, points_reserved=reward.points_cost)
            PointsTransaction.objects.create(user=request.user, amount=-reward.points_cost,
                transaction_type=PointsTransaction.SPEND, description=f"Reserved for {reward.name} (claim #{claim.pk})")
            messages.success(request, "Reward requested. Your points are reserved until the owner reviews it.")
    return redirect("reward_catalogue")

def staff_required(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(staff_required, login_url="login")
def owner_dashboard(request):
    context = {
        "customer_count": CustomerProfile.objects.count(),
        "code_count": ProductCode.objects.count(),
        "redeemed_count": ProductCode.objects.filter(is_redeemed=True).count(),
        "points_issued": PointsTransaction.objects.filter(transaction_type=PointsTransaction.EARN).aggregate(v=Sum("amount"))["v"] or 0,
        "pending_count": RewardClaim.objects.filter(status=RewardClaim.PENDING).count(),
        "claims": RewardClaim.objects.select_related("user", "reward").order_by("-requested_at")[:20],
        "rewards": Reward.objects.all().order_by("-created_at")[:8],
    }
    return render(request, "owner.html", context)

@user_passes_test(staff_required, login_url="login")
def generate_codes(request):
    if request.method != "POST": return redirect("owner_dashboard")
    try: quantity = int(request.POST.get("quantity", "10"))
    except ValueError: quantity = 0
    if quantity < 1 or quantity > 500:
        messages.error(request, "Choose a batch size from 1 to 500.")
        return redirect("owner_dashboard")
    alphabet = string.ascii_uppercase + string.digits
    created = []
    while len(created) < quantity:
        code = "".join(secrets.choice(alphabet) for _ in range(12))
        obj, was_created = ProductCode.objects.get_or_create(code=code, defaults={"points_value": 10})
        if was_created: created.append(code)
    output = StringIO()
    writer = csv.writer(output); writer.writerow(["product_code", "points_value"])
    for code in created: writer.writerow([code, 10])
    response = HttpResponse(output.getvalue(), content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="perkbox-code-batch.csv"'
    messages.success(request, f"Generated {quantity} unique codes. Keep the downloaded CSV secure.")
    return response

@user_passes_test(staff_required, login_url="login")
def process_claim(request, claim_id, decision):
    if request.method != "POST" or decision not in ("approve", "reject"):
        return redirect("owner_dashboard")
    with transaction.atomic():
        claim = RewardClaim.objects.select_for_update().select_related("reward").get(pk=claim_id)
        if claim.status != RewardClaim.PENDING:
            messages.warning(request, "This claim has already been processed.")
        elif decision == "approve":
            reward = Reward.objects.select_for_update().get(pk=claim.reward_id)
            if reward.stock < 1:
                messages.error(request, "No stock remains. Reject this claim to refund the customer's points.")
            else:
                reward.stock -= 1; reward.save(update_fields=["stock"])
                claim.status = RewardClaim.APPROVED
                claim.processed_by = request.user; claim.processed_at = timezone.now()
                claim.save(update_fields=["status", "processed_by", "processed_at"])
                messages.success(request, f"Claim #{claim.pk} approved.")
        else:
            profile = CustomerProfile.objects.select_for_update().get(user=claim.user)
            profile.points += claim.points_reserved; profile.save(update_fields=["points"])
            PointsTransaction.objects.create(user=claim.user, amount=claim.points_reserved,
                transaction_type=PointsTransaction.REFUND, description=f"Refund for rejected claim #{claim.pk}")
            claim.status = RewardClaim.REJECTED
            claim.processed_by = request.user; claim.processed_at = timezone.now()
            claim.save(update_fields=["status", "processed_by", "processed_at"])
            messages.success(request, f"Claim #{claim.pk} rejected and points refunded.")
    return redirect("owner_dashboard")
