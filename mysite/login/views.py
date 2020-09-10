# -*- coding:utf-8 -*-
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from . import models
from io import BytesIO
from .create_code import create_validate_code
from django.http import HttpResponse
import hashlib
import datetime
from django.conf import settings
from django.core.mail import EmailMultiAlternatives


# Create your views here.
def check_code(request):
    streamIO = BytesIO()
    img, code = create_validate_code()
    img.save(streamIO, 'PNG')
    request.session['valid_code'] = code
    print('验证码：', code)
    return HttpResponse(streamIO.getvalue())


def hash_code(s, salt='mysite'):
    h = hashlib.sha256()
    s = s + salt
    h.update(s.encode())
    return h.hexdigest()


def make_confirm_string(user):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    code = hash_code(user.name, now)
    models.ConfirmString.objects.create(code=code, user=user)
    return code


def send_mail(email, code):
    subject = '来自CMDB的注册确认邮件'
    text_content = '''感谢注册CMDB！如果您看到这条消息，说明您的邮箱服务器不提供HTML链接功能，请联系管理员！'''
    html_content = '''<p>感谢注册</p><a href="http://{}/confirm/?code={}" target=blank>CMDB</a>，欢迎您的注册！<p>请点击站点链接完成注册确认！\
                    </p><p>此链接有效期{}天！</p>'''.format('127.0.0.1:8080', code, settings.CONFIRM_DAYS)
    msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


@csrf_exempt
def login(request):
    if request.session.get('is_login',None):
        return redirect('loginapp:index')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        code = request.POST.get('check_code')
        p = request.POST.get('p')
        print('登陆验证：', username, password, code)
        if username.strip() and password:
            try:
                user = models.User.objects.get(name=username)
            except:
                message = '用户不存在'
                return render(request, 'login/login.html', {'message': message})

            if not user.has_confirmed:
                message = '该用户还未经过邮件确认！'
                return render(request, 'login/login.html', locals())
            if code.upper() == request.session.get('valid_code').upper():
                if user.password == hash_code(password):
                    request.session['is_login'] = True
                    request.session['user_id'] = user.id
                    request.session['user_name'] = user.name
                    return redirect('loginapp:index')
                else:
                    message = '密码不正确'
                    return render(request, 'login/login.html', {'message': message})
            else:
                message = '验证码错误'
                return render(request, 'login/login.html', {'message': message})
        else:
            message = '用户名或密码不为空'
            return render(request, 'login/login.html', {'message': message})
    return render(request, 'login/login.html')


def index(request):
    if not request.session.get('is_login', None):
        return redirect('loginapp:login')
    return render(request, 'login/index.html')


def register(request):
    if request.session.get('is_login', None):
        return redirect('loginapp:index')
    if request.method == 'POST':
        username = request.POST.get('username')
        password1 = request.POST.get('password')
        password2 = request.POST.get('password2')
        email = request.POST.get('email')
        sex = request.POST.get('sex')
        print(username, password1, password2, email, sex)
        if password1 != password2:
            message = '两次输入密码不正确！'
            return render(request, 'login/register.html', {'message': message})
        else:
            same_user_name = models.User.objects.filter(name=username)
            if same_user_name:
                message = '该用户名已存在！'
                return render(request, 'login/register.html', {'message': message})
            same_user_email = models.User.objects.filter(email=email)
            if same_user_email:
                message = '该邮箱已被注册！'
                return render(request, 'login/register.html', {'message': message})
            new_user = models.User()
            new_user.name = username
            new_user.password = hash_code(password1)
            new_user.email = email
            new_user.sex = sex
            new_user.save()

            code = make_confirm_string(new_user)
            send_mail(email, code)
            print(new_user.name, '成功注册')
            return render(request, 'login/login.html')
    return render(request, 'login/register.html')


def logout(request):
    if not request.session.get('is_login', None):
        return redirect('loginapp:login')
    request.session.flush()
    return redirect('loginapp:login')


def user_confirm(request):
    code = request.GET.get('code', None)
    message = ''
    try:
        confirm = models.ConfirmString.objects.get(code=code)
    except:
        message = '无效的请求！'
        return render(request, 'login/confirm.html', locals())

    c_time = confirm.create_time
    _now = datetime.datetime.now()
    if _now > c_time + datetime.timedelta(settings.CONFIRM_DAYS):
        confirm.user.delete()
        message = '您的邮件已过期！请重新注册！'
        return render(request, 'login/confirm.html', locals())
    else:
        confirm.user.has_confirmed = True
        confirm.user.save()
        confirm.delete()
        message = '感谢确认，请使用账户登录！'
        return render(request, 'login/confirm.html', locals())
