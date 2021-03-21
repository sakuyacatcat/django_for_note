from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class CustomUser(AbstractUser):
    email = models.CharField(verbose_name='メールアドレス', max_length=100)
    password = models.CharField(verbose_name='パスワード', max_length=100)

    def __str__(self):
        return self.username


class PremiumCustomer(models.Model):
    user = models.ForeignKey(
        CustomUser, verbose_name='user', related_name='user', on_delete=models.CASCADE)
    stripeCustomerId = models.CharField(max_length=255)
    stripeSubscriptionId = models.CharField(max_length=255)
    is_continued = models.BooleanField(verbose_name='次月継続', default=True)

    def __str__(self):
        return self.user.username
