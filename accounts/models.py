from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class CustomUser(AbstractUser):
    email = models.CharField(verbose_name='メールアドレス', max_length=100)
    password = models.CharField(verbose_name='パスワード', max_length=100)

    def __str__(self):
        return self.username
