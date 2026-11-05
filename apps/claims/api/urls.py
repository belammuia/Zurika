
from rest_framework.routers import DefaultRouter
from .views import ClaimViewSet,SupportingDocumentViewSet

router = DefaultRouter()
router.register("claims", ClaimViewSet, basename="claim")
router.register("documents", SupportingDocumentViewSet, basename="supporting-document")

urlpatterns = router.urls
