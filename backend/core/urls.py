from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('pricing/', include('apps.pricing.api.routers')),
    path('download-schema/', SpectacularAPIView.as_view(), name='download-schema'),  # Agrega esta línea
    path('swagger/', SpectacularSwaggerView.as_view(url_name='download-schema')),  # http://localhost:8000/swagger/
    path('redoc/', SpectacularRedocView.as_view(url_name='download-schema')),  # http://localhost:8000/redoc/
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
