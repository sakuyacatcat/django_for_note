from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField

# Create your models here.


class PostModel(models.Model):
    title = models.CharField(max_length=255)
    content = RichTextUploadingField(blank=True, null=True)
    # content = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
