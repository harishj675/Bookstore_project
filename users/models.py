from django.contrib.auth.models import User
from django.db import models


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
