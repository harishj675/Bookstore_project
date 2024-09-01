from django.contrib.auth.models import User
from rest_framework import serializers

from ..models import UserProfile, Notifications


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['roll', 'address', 'mobile_number', 'pincode']


class UserSerializers(serializers.ModelSerializer):
    profile = UserProfileSerializer()

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'profile']


class CreateUserSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notifications
        fields = ['id', 'message', 'timestamp', 'is_read']
