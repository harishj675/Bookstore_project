from rest_framework import permissions

from .models import UserProfile


class IsOwnerOrManager(permissions.BasePermission):
    """
    Custom permission to allow:
    - Owners to delete the review.
    - Managers to update and delete the review.
    """

    def has_object_permission(self, request, view, obj):
        user_profile = UserProfile.objects.get(user_id=request.user.id)
        # Allow read permissions to any request (safe methods are GET, HEAD, or OPTIONS).
        if request.method in permissions.SAFE_METHODS:
            return True

        # Allow deletion if the user is the owner or a manager.
        if request.method == 'DELETE':
            return obj.user == request.user or user_profile.roll == 'Manager' or user_profile.roll == 'staff'

        # Allow update only if the user is a manager.
        if request.method in ['PUT', 'PATCH']:
            return user_profile.roll == 'Manager' or user_profile.roll == 'staff'

        # For any other method, deny access.
        return False


class IsStaffOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow staff members to edit or delete books.
    """

    def has_permission(self, request, view):
        user_profile = UserProfile.objects.get(user_id=request.user.id)
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.method == 'DELETE':
            return user_profile.roll == 'Manager'

        if request.method in ['PUT', 'PATCH', 'POST']:
            return user_profile.roll == 'Manager' or user_profile.roll == 'Staff'


class IsStaffUser(permissions.BasePermission):
    """
    Custom permission to only allow staff users to access the view.
    """

    def has_permission(self, request, view):
        user_profile = UserProfile.objects.get(user_id=request.user.id)
        return user_profile.roll == 'Manager' or user_profile.roll == 'Staff'
