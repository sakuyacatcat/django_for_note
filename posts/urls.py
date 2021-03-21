from django.urls import path
from .views import PostDetail, save_history, like

urlpatterns = [
    path('<int:pk>/', save_history, name='save_history'),
    path('<int:pk>/detail/', PostDetail.as_view(), name='post_detail'),
    path('<int:pk>/detail/like', like, name='like'),
]
