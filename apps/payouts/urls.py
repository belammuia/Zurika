from django.urls import path

from .views import MpesaResultView, MpesaTimeoutView

urlpatterns = [
    path("mpesa/result/<str:secret>/", MpesaResultView.as_view()),
    path("mpesa/timeout/<str:secret>/", MpesaTimeoutView.as_view()),
]