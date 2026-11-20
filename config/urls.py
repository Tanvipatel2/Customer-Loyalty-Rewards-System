from django.contrib import admin
from django.urls import path, include
from rewards import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/register/", views.register, name="register"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("redeem/", views.redeem_code, name="redeem"),
    path("rewards/", views.reward_catalogue, name="reward_catalogue"),
    path("rewards/claim/<int:reward_id>/", views.claim_reward, name="claim_reward"),
    path("owner/", views.owner_dashboard, name="owner_dashboard"),
    path("owner/codes/generate/", views.generate_codes, name="generate_codes"),
    path("owner/claims/<int:claim_id>/<str:decision>/", views.process_claim, name="process_claim"),
]
