from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


# Create your models here.

class UserProfile(models.Model):
    ROLL_CHOICES = [
        ('User', 'User'),
        ('Staff', 'Staff'),
        ('Manager', 'Manager'),
    ]

    def __str__(self):
        return self.user.first_name

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    roll = models.CharField(max_length=50, choices=ROLL_CHOICES, default='User')
    address = models.CharField(max_length=100, null=True, blank=True)
    mobile_number = models.CharField(null=True, blank=True)
    pincode = models.IntegerField(null=True, blank=True)


class Notifications(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notification')
    message = models.TextField()
    url = models.URLField(null=True, blank=True)
    is_read = models.URLField(default=False)
    timestamp = models.DateTimeField(default=timezone.now)
