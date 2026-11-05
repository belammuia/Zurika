from django.urls import path

from .views import (
    MpesaResultView,
    MpesaTimeoutView,
    MpesaStatusResultView,
    MpesaStatusTimeoutView,
)

urlpatterns = [
    path("mpesa/result/<str:secret>/", MpesaResultView.as_view()),
    path("mpesa/timeout/<str:secret>/", MpesaTimeoutView.as_view()),
    path(
        "mpesa/status-result/<str:secret>/",
        MpesaStatusResultView.as_view(),
    ),
    path(
        "mpesa/status-timeout/<str:secret>/",
        MpesaStatusTimeoutView.as_view(),
    ),
]