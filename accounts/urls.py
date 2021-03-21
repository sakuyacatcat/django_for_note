from django.urls import path
from .views import Toppage, Create, Login, Logout, Delete, Mypage, PremiumCheckout, stripe_config, stripe_webhook

urlpatterns = [
    path('', Toppage.as_view(), name='toppage'),
    path('create/', Create.as_view(), name='create'),
    path('login/', Login.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),
    path('delete/', Delete.as_view(), name='delete'),
    path('mypage/', Mypage.as_view(), name='mypage'),
    path('mypage/config/', stripe_config, name='config'),
    path('mypage/checkout/', PremiumCheckout.as_view(), name='checkout'),
    path('webhook/', stripe_webhook, name='webhook'),
]
