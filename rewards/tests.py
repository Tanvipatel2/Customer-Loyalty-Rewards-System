from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import CustomerProfile, ProductCode, PointsTransaction, Reward, RewardClaim

class LoyaltyFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="customer", password="StrongPass123!")
        self.profile = CustomerProfile.objects.get(user=self.user)
        self.client = Client()
        self.client.login(username="customer", password="StrongPass123!")
    def test_valid_code_adds_points_once(self):
        ProductCode.objects.create(code="ABCD1234EFGH", points_value=10)
        self.client.post(reverse("redeem"), {"code": "abcd-1234-efgh"})
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.points, 10)
        self.assertEqual(PointsTransaction.objects.filter(user=self.user).count(), 1)
    def test_reuse_code_does_not_add_points_twice(self):
        ProductCode.objects.create(code="ABCD1234EFGH", points_value=10)
        self.client.post(reverse("redeem"), {"code": "ABCD1234EFGH"})
        self.client.post(reverse("redeem"), {"code": "ABCD1234EFGH"})
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.points, 10)
        self.assertEqual(PointsTransaction.objects.filter(user=self.user).count(), 1)
    def test_reward_claim_reserves_points(self):
        self.profile.points = 100; self.profile.save()
        reward = Reward.objects.create(name="Bottle", description="Steel bottle", points_cost=60, stock=3)
        self.client.post(reverse("claim_reward", args=[reward.pk]))
        self.profile.refresh_from_db()
        claim = RewardClaim.objects.get(user=self.user)
        self.assertEqual(self.profile.points, 40)
        self.assertEqual(claim.status, RewardClaim.PENDING)
        self.assertEqual(reward.stock, 3)
    def test_staff_approval_reduces_stock(self):
        staff = User.objects.create_user(username="owner", password="StrongPass123!", is_staff=True)
        reward = Reward.objects.create(name="Bag", description="Bag", points_cost=20, stock=2)
        claim = RewardClaim.objects.create(user=self.user, reward=reward, points_reserved=20)
        self.client.force_login(staff)
        self.client.post(reverse("process_claim", args=[claim.pk, "approve"]))
        reward.refresh_from_db(); claim.refresh_from_db()
        self.assertEqual(reward.stock, 1)
        self.assertEqual(claim.status, RewardClaim.APPROVED)
    def test_rejection_refunds_points_once(self):
        staff = User.objects.create_user(username="owner", password="StrongPass123!", is_staff=True)
        reward = Reward.objects.create(name="Bag", description="Bag", points_cost=20, stock=2)
        self.profile.points = 5; self.profile.save()
        claim = RewardClaim.objects.create(user=self.user, reward=reward, points_reserved=20)
        self.client.force_login(staff)
        self.client.post(reverse("process_claim", args=[claim.pk, "reject"]))
        self.client.post(reverse("process_claim", args=[claim.pk, "reject"]))
        self.profile.refresh_from_db(); claim.refresh_from_db()
        self.assertEqual(self.profile.points, 25)
        self.assertEqual(claim.status, RewardClaim.REJECTED)
