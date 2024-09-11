from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

# Schema view for API documentation
schema_view = SpectacularAPIView.as_view()

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('', include('bookstore.urls')),
                  path('accounts/', include('django.contrib.auth.urls')),
                  path('users/', include('users.urls')),
                  path('cart/', include('cart.urls')),
                  path('api/bookstore/', include('bookstore.api.urls')),
                  path('api/users/', include('users.api.urls')),
                  path('api/cart/', include('cart.api.urls')),

                  path('api/schema/', schema_view, name='schema'),
                  path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
                  path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
