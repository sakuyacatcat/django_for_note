from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField
from accounts.models import CustomUser

# Create your models here.


class Category(models.Model):
    parent = models.ForeignKey(
        'self', related_name='children', on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class PostModel(models.Model):
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255)
    content = RichTextUploadingField(blank=True, null=True)
    price = models.IntegerField(default=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class PostBuyHistory(models.Model):
    post = models.ForeignKey(
        PostModel, verbose_name='購入記事', on_delete=models.CASCADE)
    user = models.ForeignKey(
        CustomUser, verbose_name='購入者', on_delete=models.CASCADE)
    stripe_id = models.CharField(verbose_name='購入情報', max_length=255)
    created_at = models.DateTimeField(verbose_name='購入日', auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.created_at.strftime('%Y/%m/%d %H:%M:%S')+'　'+self.user.username+'　'+self.post.title


class History(models.Model):
    user = models.ForeignKey(
        CustomUser, verbose_name='user', blank=True, on_delete=models.CASCADE)
    post = models.ForeignKey(
        PostModel, verbose_name='post', blank=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.created_at.strftime('%Y/%m/%d %H:%M:%S')+'　'+self.user.username+'　'+self.post.title


class Like(models.Model):
    user = models.ForeignKey(
        CustomUser, verbose_name='user', blank=True, on_delete=models.CASCADE)
    post = models.ForeignKey(
        PostModel, verbose_name='post', blank=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.created_at.strftime('%Y/%m/%d %H:%M:%S')+'　'+self.user.username+'　'+self.post.title
