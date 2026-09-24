from rest_framework.routers import DefaultRouter

from .views import ClientViewSet, VehicleViewSet

router = DefaultRouter()
router.register("vehicles",VehicleViewSet, basename="vehicle")
router.register("", ClientViewSet, basename="client")

urlpatterns = router.urls