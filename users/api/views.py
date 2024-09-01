from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .serializers import UserSerializers, CreateUserSerializers, NotificationSerializer
from ..models import Notifications


class CheckPoint(APIView):

    def get(self, request):
        return Response({
            "message": "API hits right place"
        }, status=200)


class UserModelView(ModelViewSet):
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateUserSerializers
        return UserSerializers

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"detail": f"User '{instance.username}' was successfully deleted."},
            status=status.HTTP_204_NO_CONTENT
        )

    def perform_destroy(self, instance):
        instance.delete()


class NotificationListAPIView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Notifications.objects.filter(user_id=user.id, is_read=False).order_by('-timestamp')


class MarkAsReadAPIView(APIView):
    def patch(self, request, notification_id, *args, **kwargs):
        try:
            notification = Notifications.objects.get(pk=notification_id)
            notification.is_read = True
            notification.save()
            return Response({'status': 'Notification marked as read'}, status=status.HTTP_200_OK)
        except Notifications.DoesNotExist:
            return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f'Error in setting notification as read: {e}')
            return Response({'error': 'An error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
