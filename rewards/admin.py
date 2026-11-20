from django.contrib import admin
from .models import CustomerProfile, ProductCode, PointsTransaction, Reward, RewardClaim

@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "points", "joined_at")
    search_fields = ("user__username", "user__email")
@admin.register(ProductCode)
class ProductCodeAdmin(admin.ModelAdmin):
    list_display = ("code", "points_value", "is_redeemed", "redeemed_by", "redeemed_at")
    list_filter = ("is_redeemed",)
    search_fields = ("code", "redeemed_by__username")
@admin.register(PointsTransaction)
class PointsTransactionAdmin(admin.ModelAdmin):
    list_display = ("user", "amount", "transaction_type", "description", "created_at")
    list_filter = ("transaction_type",)
@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    list_display = ("name", "points_cost", "stock", "active")
    list_editable = ("stock", "active")
@admin.register(RewardClaim)
class RewardClaimAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "reward", "points_reserved", "status", "requested_at")
    list_filter = ("status",)
