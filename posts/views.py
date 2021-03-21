from django.views.generic import DetailView
from django.shortcuts import render, redirect
from .models import PostModel, History, Like, PostBuyHistory
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.conf import settings

import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

# Create your views here.


class PostDetail(DetailView):
    model = PostModel
    template_name = 'post.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data()
        if self.request.user.is_authenticated:
            context["like"] = Like.objects.filter(
                Q(user=self.request.user) & Q(post=self.object))
            context["public_key"] = settings.STRIPE_PUBLIC_KEY
            context["is_bought"] = PostBuyHistory.objects.filter(
                Q(user=self.request.user) & Q(post=self.object))
        return context

    def post(self, request, *args, **kwargs):
        post = self.get_object()
        token = request.POST['stripeToken']  # フォームでのサブミット後に自動で作られる
        try:
            # 購入処理
            charge = stripe.Charge.create(
                amount=post.price,
                currency='jpy',
                source=token,
                description='メール:{} 購入記事名:{}'.format(
                    request.user.email, post.title),
            )
        except stripe.error.CardError as e:
            # カード決済が上手く行かなかった(限度額超えとか)ので、メッセージと一緒に再度ページ表示
            context = self.get_context_data()
            context['message'] = 'Your payment cannot be completed. The card has been declined.'
            return render(request, 'post.html', context)
        else:
            # 上手く購入できた。Django側にも購入履歴を入れておく
            PostBuyHistory.objects.create(
                post=post, user=self.request.user, stripe_id=charge.id)
            return redirect('post_detail', pk=self.kwargs['pk'])


def save_history(request, pk):
    if request.user.is_authenticated:
        user = request.user
        look_post = PostModel.objects.get(pk=pk)
        history = History.objects.filter(Q(user=user) & Q(post=look_post))

        if history:
            history.delete()
            history = History.objects.create(user=user, post=look_post)
        else:
            history = History.objects.create(user=user, post=look_post)

    return redirect('post_detail', pk=pk)


@login_required(login_url='/accounts/login/')
def like(request, pk):
    post = PostModel.objects.get(pk=pk)
    user = request.user
    like_object = Like.objects.filter(Q(user=user) & Q(post=post))
    if like_object:
        like_object.delete()
    else:
        like_object = Like.objects.create(user=user, post=post)
    return redirect('post_detail', pk=pk)
