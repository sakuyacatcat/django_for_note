from django.views import View
from django.views.generic import TemplateView
# from django import template
from django.shortcuts import render, redirect
from django.urls import reverse

from .models import CustomUser
from .forms import CreateForm, LoginForm

from django.contrib.auth import login as auth_login, logout as auth_logout

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
