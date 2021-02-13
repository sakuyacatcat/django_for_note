from django.urls import path
from .views import PostDetail

urlpatterns = [
    path('<int:pk>/detail/', PostDetail.as_view(), name='post_detail'),
]
