# coding:UTF-8
import random
import string
import threading
from django.shortcuts import render,redirect
from django.contrib import auth
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.urls import reverse
from django.http import JsonResponse
from captcha.models import CaptchaStore 
from captcha.helpers import captcha_image_url
from .forms import LoginForm,RegForm,ChangeNicknameForm,BindEmailForm,ChangePasswordForm,ResetPasswordForm
from .models import Profile,UserConfig
from mysite.settings import EMAIL_HOST_USER

def login(request):
    if request.is_ajax():
        result = dict()
        result['key'] = CaptchaStore.generate_key()
        result['image_url'] = captcha_image_url(result['key'])
        return JsonResponse(result)
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user = login_form.cleaned_data['user']
            auth.login(request,user)
            return redirect(request.GET.get('from',reverse('home')))
    else:
        login_form = LoginForm()
    return render(request,'user/login.html',{'login_form':login_form})

def logout(request):
    auth.logout(request)
    return redirect(request.GET.get('from',reverse('home')))


def login_for_modal(request,status='submit'):
    if status == 'refresh':
        result = dict()
        result['key'] = CaptchaStore.generate_key()
        result['image_url'] = captcha_image_url(result['key'])
        return JsonResponse(result)

    login_form = LoginForm(request.POST)
    data = {}
    
    if login_form.is_valid():
        user = login_form.cleaned_data['user']
        auth.login(request,user)
        data['status'] = "SUCCESS"
    else:
        data['status'] = "ERROR"
        is_error_in_captcha = True if 'captcha' in login_form.errors else False
        is_error_in_all = True if '__all__' in login_form.errors else False
        #用户名或密码错误且验证码错误
        if is_error_in_all and is_error_in_captcha:
            data['code'] = 400
        #仅用户名或密码错误
        elif is_error_in_all:
            data['code'] = 401
        #仅验证码错误
        else:
            data['code'] = 402
        '''
        print(login_form.errors['captcha'].as_text())
        print(login_form.errors['__all__'].as_text())
        '''
    return JsonResponse(data)
            


def register(request):
    if request.is_ajax():
        result = dict()
        result['key'] = CaptchaStore.generate_key()
        result['image_url'] = captcha_image_url(result['key'])
        return JsonResponse(result)
    if request.method == 'POST':
        reg_form = RegForm(request.POST,request=request)
        if reg_form.is_valid():
            username = reg_form.cleaned_data['username']
            password = reg_form.cleaned_data['password']
            email = reg_form.cleaned_data['email']
            user = User.objects.create_user(username,email,password)
            user.save()
            # 创建该用户的配置 默认关闭邮件通知
            user_config = UserConfig()
            user_config.user = user
            user_config.save()
            del request.session['register_code']
            user = auth.authenticate(username = username,password = password)
            auth.login(request,user)
            return redirect(request.GET.get('from',reverse('home')))
    else:
        reg_form = RegForm()
    return render(request,'user/register.html',{'reg_form':reg_form})

def change_nickname(request):
    redirect_to = request.GET.get('from',reverse('home'))

    if request.method == 'POST':
        form = ChangeNicknameForm(request.POST,user=request.user)
        if form.is_valid():
            user = form.cleaned_data['user']
            new_nickname = form.cleaned_data['new_nickname']
            profile,created = Profile.objects.get_or_create(user=user)
            profile.nickname =new_nickname
            profile.save()
            return redirect(redirect_to)
    else:
        form = ChangeNicknameForm()
    context = {}
    context['index_title'] = '修改昵称'
    context['form_title'] = '修改昵称'
    context['submit_text'] = '修改'
    context['form'] = form
    context['return_back_to'] = redirect_to
    return render(request,'form.html',context)

def user_info(request,user_pk):
    user_visited = User.objects.get(pk=user_pk)
    context = {}
    context['user_visited'] = user_visited
    return render(request,'user/user_info.html',context)

def bind_email(request):
    redirect_to = request.GET.get('from',reverse('home'))
    if request.method == 'POST':
        form = BindEmailForm(request.POST,request=request)
        if form.is_valid():
            user = request.user
            user.email = form.cleaned_data['email']
            user.save()
            del request.session['bind_email_code']
            return redirect(redirect_to)
    else:
        form = BindEmailForm()
    context = {}
    context['index_title'] = '绑定邮箱'
    context['form_title'] = '绑定邮箱'
    context['submit_text'] = '绑定'
    context['form'] = form
    context['return_back_to'] = redirect_to
    return render(request,'user/bind_email_form.html',context)

class SendEmail(threading.Thread):
    def __init__(self,subject,text,email,fail_silently=False):
        self.subject = subject
        self.text = text
        self.email = email
        self.fail_silently = fail_silently
        threading.Thread.__init__(self)


    def run(self):
        send_mail(
            self.subject,
            self.text,
            EMAIL_HOST_USER,
            [self.email],
            fail_silently = self.fail_silently,
        )

def send_validation_code(request):
    data = {}
    title = ''
    email = request.GET.get('email','')
    code_key = request.GET.get('type','')
    if code_key != 'reset_password_code':
        if User.objects.filter(email=email).exists():
            data['status'] = 'ERROR'
            data['code'] = 399
            return JsonResponse(data)
    if code_key == 'reset_password_code':
        title = '重置密码邮箱验证'
    elif code_key == 'bind_email_code':
        title = '绑定邮箱验证'
    elif code_key == 'register_code':
        title = '注册邮箱验证'
    #随机生成验证码并存入session
    validation_code = ''.join(random.sample(string.ascii_letters+string.digits,4))
    request.session[code_key] = validation_code
    # 邮箱不为空才处理
    # 多线程处理
    if email != '':
        SendEmail(title,validation_code,email).start()
        data['status'] = 'SUCCESS'
    else:
        data['status'] = 'ERROR'
        data['code'] = 400
    return JsonResponse(data)

def change_password(request):
    redirect_to = reverse('login')
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST,user=request.user)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            request.user.set_password(new_password)
            request.user.save()
            auth.logout(request)
            return redirect(redirect_to)
    else:
        form = ChangePasswordForm()

    context = {}
    context['index_title'] = '修改密码'
    context['form_title'] = '修改密码'
    context['submit_text'] = '修改'
    context['form'] = form
    context['return_back_to'] = redirect_to
    return render(request,'form.html',context)    

def reset_password(request):
    redirect_to = reverse('home')
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST,request=request)
        if form.is_valid():
            user = form.cleaned_data['user']
            new_password = form.cleaned_data['new_password']
            print(new_password)
            user.set_password(new_password)
            user.save()
            del request.session['reset_password_code']
            return redirect(redirect_to)
    else:
        form = ResetPasswordForm()
    context = {}
    context['index_title'] = '重置密码'
    context['form_title'] = '重置密码'
    context['submit_text'] = '重置'
    context['form'] = form
    context['return_back_to'] = redirect_to
    return render(request,'user/reset_password.html',context)

def user_config(request):
    if request.is_ajax():
        status = request.GET.get('status','')
        data = {}
        print(status)
        if status != '':
            user_config = UserConfig.objects.get(user=request.user)
            user_config.is_email_active = True if status == 'true' else False
            user_config.save()
            data['status'] = "SUCCESS"
        else:
            data['status'] = "ERROR"
        return JsonResponse(data)
    else:
        return render(request,'user/user_config.html',{})





