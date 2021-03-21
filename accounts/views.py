from django.views import View
from django.views.generic import TemplateView
# from django import template
from django.shortcuts import render, redirect
from django.urls import reverse

from .models import CustomUser, PremiumCustomer
from .forms import CreateForm, LoginForm

from django.contrib.auth import login as auth_login, logout as auth_logout

from posts.models import PostModel, Category, Like, History
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Q
from itertools import chain

from django.conf import settings
from django.http.response import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import time
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

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
        # ログインユーザーが有料会員ならモデルのデータ・有効期限を取得して渡す
        if PremiumCustomer.objects.filter(user=self.request.user):
            premium_customer = PremiumCustomer.objects.get(
                user=self.request.user)
            subscription = stripe.Subscription.retrieve(
                premium_customer.stripeSubscriptionId)
            period_end = time.strftime("%Y年%m月%d日", time.localtime(
                subscription['current_period_end']))
            return render(request, 'mypage.html', {
                'premium_customer': premium_customer,
                'subscription': subscription,
                'period_end': period_end
            })
        # 有料会員でない場合は処理なしでrender
        return render(request, 'mypage.html')

    # def get(self, request, *args, **kwargs):
    #     # 1/14　髙木更新　Like、Historyをモデルに変更により、context作成のアルゴリズム変更
    #     likes = Like.objects.filter(user=request.user).order_by('-created_at')
    #     histories = History.objects.filter(
    #         user=request.user).order_by('-created_at')
    #     recommend_posts = PostModel.objects.none()
    #     cats = []
    #     histories_for_recommend = histories.order_by('-created_at')[:3]

    #     for history in histories_for_recommend:
    #         cat = history.post.category
    #         cats.append(cat)
    #     cats_unique = list(set(cats))

    #     # 12/30　recommend_postsのクエリセットにカテゴリーから取得したオススメ記事のクエリセットを結合(chain関数　インポート必要)
    #     for cat in cats_unique:
    #         posts = PostModel.objects.filter(
    #             category=cat).order_by('-created_at')[:3]
    #         recommend_posts = chain(recommend_posts, posts)

    #     return render(request, 'mypage.html', {'likes': likes, 'histories': histories, 'recommend_posts': recommend_posts})


def stripe_config(request):
    if request.method == 'GET':
        stripe_config = {'publicKey': settings.STRIPE_PUBLIC_KEY}
        return JsonResponse(stripe_config, safe=False)


class PremiumCheckout(View):
    def get(self, request, *args, **kwargs):
        domain_url = 'http://127.0.0.1:8000/'
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            checkout_session = stripe.checkout.Session.create(
                client_reference_id=request.user.id if request.user.is_authenticated else None,
                success_url=domain_url + 'accounts/mypage/',
                cancel_url=domain_url + 'accounts/mypage/',
                payment_method_types=['card'],
                mode='subscription',
                line_items=[
                    {
                        'price': settings.STRIPE_PRICE_ID,
                        'quantity': 1,
                    }
                ]
            )
            return JsonResponse({'sessionId': checkout_session['id']})
        except Exception as e:
            return JsonResponse({'error': str(e)})


@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
    payload = request.body.decode('utf-8')
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        # Fetch all the required data from session
        client_reference_id = session.get('client_reference_id')
        stripe_customer_id = session.get('customer')
        stripe_subscription_id = session.get('subscription')

        # Get the user and create a new StripeCustomer
        user = CustomUser.objects.get(pk=client_reference_id)
        PremiumCustomer.objects.create(
            user=user, stripeCustomerId=stripe_customer_id, stripeSubscriptionId=stripe_subscription_id)

    return HttpResponse(status=200)
