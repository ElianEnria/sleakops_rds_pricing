from rest_framework.routers import DefaultRouter

from apps.pricing.api.views.general_views import PriceViewSet, ProductViewSet

router = DefaultRouter()
router.register(r'', PriceViewSet, basename='price')
router.register(r'product', ProductViewSet, basename='product')


urlpatterns = router.urls