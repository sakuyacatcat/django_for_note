from django.views.generic import DetailView
from django.shortcuts import render
from .models import PostModel

# Create your views here.


class PostDetail(DetailView):
    model = PostModel
    template_name = 'post.html'
