from django.conf import settings
from django.db import models
from django.utils import timezone

class CustomerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    points = models.PositiveIntegerField(default=0)
    joined_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"{self.user.username} · {self.points} points"

class ProductCode(models.Model):
    code = models.CharField(max_length=20, unique=True)
    points_value = models.PositiveIntegerField(default=10)
    is_redeemed = models.BooleanField(default=False)
    redeemed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="redeemed_codes")
    redeemed_at = models.DateTimeField(null=True, blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"{self.code} ({'used' if self.is_redeemed else 'unused'})"

class PointsTransaction(models.Model):
    EARN = "EARN"; SPEND = "SPEND"; REFUND = "REFUND"
    TYPES = [(EARN, "Earned"), (SPEND, "Spent"), (REFUND, "Refunded")]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="point_transactions")
    amount = models.IntegerField()
    transaction_type = models.CharField(max_length=10, choices=TYPES)
    description = models.CharField(max_length=220)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"{self.user} {self.amount:+} pts"

class Reward(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    points_cost = models.PositiveIntegerField()
    stock = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.name

class RewardClaim(models.Model):
    PENDING = "PENDING"; APPROVED = "APPROVED"; REJECTED = "REJECTED"
    STATUS = [(PENDING, "Pending"), (APPROVED, "Approved"), (REJECTED, "Rejected")]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reward_claims")
    reward = models.ForeignKey(Reward, on_delete=models.PROTECT, related_name="claims")
    points_reserved = models.PositiveIntegerField()
    status = models.CharField(max_length=10, choices=STATUS, default=PENDING)
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    processed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="processed_claims")
    staff_note = models.CharField(max_length=250, blank=True)
    def __str__(self): return f"#{self.pk} {self.reward.name} · {self.status}"
