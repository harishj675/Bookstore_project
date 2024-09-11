from django.urls import path, include
from rest_framework.authtoken import views
from rest_framework.routers import DefaultRouter

from .views import UserModelView, NotificationListAPIView, MarkAsReadAPIView

router = DefaultRouter()
router.register(r'user', UserModelView)

urlpatterns = [
    path('login/', views.obtain_auth_token, name='user-login'),
    path('', include(router.urls)),
    path('notifications/', NotificationListAPIView.as_view(), name='notifications_list'),
    path('notifications/mark-as-read/<int:notification_id>/', MarkAsReadAPIView.as_view(),
         name='notifications_details'),
]
