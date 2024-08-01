from django.contrib import admin
from django.contrib.auth.models import User

from .models import UserProfile

# Unregister the custom admin for User if it exists
admin.site.unregister(User)

# Re-register the default UserAdmin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin

admin.site.register(User, DefaultUserAdmin)
admin.site.register(UserProfile)
