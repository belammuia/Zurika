from rest_framework.routers import DefaultRouter

from .views import VehicleViewSet, PolicyViewSet

router = DefaultRouter()
router.register("vehicles", VehicleViewSet, basename="vehicles")
router.register("policies", PolicyViewSet, basename="policies")

urlpatterns = router.urls
