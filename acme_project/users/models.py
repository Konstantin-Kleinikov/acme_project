from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class CustomUser(AbstractUser):
    birthday = models.DateField(null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
