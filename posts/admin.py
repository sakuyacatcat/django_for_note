from django.contrib import admin
from django.db import models
from .models import PostModel, History, Like, PostBuyHistory

# Register your models here.
admin.site.register(PostModel)
admin.site.register(History)
admin.site.register(Like)
admin.site.register(PostBuyHistory)
