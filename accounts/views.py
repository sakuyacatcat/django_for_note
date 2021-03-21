from django.views import View
from django.views.generic import TemplateView
# from django import template
from django.shortcuts import render, redirect
from django.urls import reverse

from .models import CustomUser
from .forms import CreateForm, LoginForm

from django.contrib.auth import login as auth_login, logout as auth_logout

from posts.models import PostModel, Category, Like, History
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Q
from itertools import chain


# Create your views here.


class Toppage(TemplateView):
    template_name = 'toppage.html'


class Create(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('toppage')
        context = {'form': CreateForm()}
        return render(request, 'create.html', context)

    def post(self, request, *args, **kwargs):
        form = CreateForm(request.POST)
        if not form.is_valid():
            return render(request, 'create.html', {'form': form})
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()
        auth_login(request, user)
        return redirect('toppage')


# create = Create.as_view()


class Login(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('toppage')
        context = {'form': LoginForm()}
        return render(request, 'login.html', context)

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)
        if not form.is_valid():
            return render(request, 'login.html', {'form': form})
        user = form.get_user()
        auth_login(request, user)
        return redirect('toppage')


# login = Login.as_view()


class Logout(View):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        auth_logout(request)
        return redirect('toppage')


# logout = Logout.as_view()


class Delete(View):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        user = request.user
        user.delete()
        return redirect('toppage')


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class Mypage(View):
    model = CustomUser

    def get(self, request, *args, **kwargs):
        # 1/14　髙木更新　Like、Historyをモデルに変更により、context作成のアルゴリズム変更
        likes = Like.objects.filter(user=request.user).order_by('-created_at')
        histories = History.objects.filter(
            user=request.user).order_by('-created_at')
        recommend_posts = PostModel.objects.none()
        cats = []
        histories_for_recommend = histories.order_by('-created_at')[:3]

        for history in histories_for_recommend:
            cat = history.post.category
            cats.append(cat)
        cats_unique = list(set(cats))

        # 12/30　recommend_postsのクエリセットにカテゴリーから取得したオススメ記事のクエリセットを結合(chain関数　インポート必要)
        for cat in cats_unique:
            posts = PostModel.objects.filter(
                category=cat).order_by('-created_at')[:3]
            recommend_posts = chain(recommend_posts, posts)

        return render(request, 'mypage.html', {'likes': likes, 'histories': histories, 'recommend_posts': recommend_posts})
