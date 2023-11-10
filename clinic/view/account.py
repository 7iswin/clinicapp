from django.shortcuts import render,redirect
from django.urls import reverse
from django.contrib import messages
from clinic.model.account import Account
from django.contrib.auth.models import User, auth
import datetime
from django.core.mail import send_mail
import random
from django.http import JsonResponse
import time
import json
from django.conf import settings
from django.contrib.auth import update_session_auth_hash
from django.core.cache import cache
from datetime import timezone, datetime, timedelta
otp_store = {}
MAX_LOGIN_ATTEMPTS = 3
LOCKOUT_TIME_PERIOD = 1
def generate_and_send_otp(request):

    if request.method == 'POST':
        
        data = json.loads(request.body)
        email = data['email']

        if email:
            otp = str(random.randint(100000, 999999))  
            otp_store[email] = {
                'otp': otp,
                'timestamp': time.time()  
            }
            send_mail(
                'University Clinic Quezon City',
                f'Your OTP is: {otp} Dont Send this to anyone else! ',
                settings.EMAIL_USER,  
                [email],  
                fail_silently=False,
            )
            return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})

def index(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        otp = request.POST['otp']
        
        stored_data = otp_store.get(email)
        if stored_data:
            stored_otp = stored_data['otp']
            timestamp = stored_data['timestamp']
            current_time = time.time()
            if stored_otp == otp and (current_time - timestamp) <= 6000:
                if password1 != password2:
                    messages.error(request, 'Passwords do not match!')
                    return redirect(reverse('account:index'))
                
                if User.objects.filter(email=email).exists():
                    messages.error(request, 'Email already registered.')
                    return redirect(reverse('account:index'))
                
                user = User.objects.create_user(username=username, email=email, password=password1)
                user.is_active = False
                user.save()
                

                account_model = Account.objects.create(user=user)
                account_model.save()
                
                del otp_store[email]
                
                user_login = auth.authenticate(request, username=username, password=password1)
                if user_login is not None:
                    login(request, user_login)
                
                return redirect(reverse('dashboard:index'))
            else:
                messages.error(request, 'Invalid OTP or OTP has expired.')
                return redirect(reverse('account:index'))
        else:
            messages.error(request, 'OTP not found.')
            return redirect(reverse('account:index'))
    
    else:
        return render(request, 'login/login.html')
def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        attempt = request.session.get('login_attempt_count', MAX_LOGIN_ATTEMPTS)
        lockout_time = request.session.get('lockout_time', None)
        current_time = datetime.now()
        if user is not None and attempt > 0:
            if user.is_active:
                auth.login(request, user)
                request.session['login_attempt_count'] = MAX_LOGIN_ATTEMPTS
                request.session.pop('lockout_time', None) 
                messages.success(request, 'Logging into your account')
                return redirect(reverse('dashboard:index'))
        else:
            if attempt > 0:
                attempt -= 1
                messages.error(request, 'Username and Password do not match! or Your account is not active. Please contact the administrator.')
                messages.error(request, f'You have {attempt} attempt(s) remaining.')
                request.session['login_attempt_count'] = attempt
                if attempt == 0:
                    lockout_time = current_time + timedelta(hours=LOCKOUT_TIME_PERIOD)
                    remaining_time = lockout_time.ctime()

                    request.session['lockout_time'] = lockout_time.isoformat()
                   
                    messages.error(request, f'Account is locked due to too many login attempts. Please try again later. Lockout time: {remaining_time}')
                    return redirect(reverse('account:index'))
                return redirect(reverse('account:index'))
            else:
                remaining_time = datetime.fromisoformat(lockout_time) - current_time
                print(datetime.fromisoformat(lockout_time),current_time)
                if  datetime.fromisoformat(lockout_time) <= current_time:
                    request.session['login_attempt_count'] = MAX_LOGIN_ATTEMPTS
                    request.session.pop('lockout_time', None) 
                    messages.error(request, 'Username and Password do not match! or Your account is not active. Please contact the administrator.')
                    return redirect(reverse('account:index'))
                    
                messages.error(request, f'Account is locked due to too many login attempts. Please try again later. Remaining time: {remaining_time}')
                return redirect(reverse('account:index'))

    else:
        return redirect(reverse('account:index'))

          


def logout(request):
    auth.logout(request) 
    messages.success(request,'Logging out your account')
    return redirect(reverse('account:index'))


def profile(request):
    user_model = Account.objects.filter(user=request.user).first()
    context = {
        'user_model':user_model
    }

    return render(request, 'accountsetting/profile.html',context)


def edit_profile(request):
    user_model = Account.objects.filter(user=request.user).first()
    account_model = Account.objects.filter(user=request.user).first()
    
    if request.method == 'POST':
    
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        gender = request.POST['gender']
        profileimg = request.FILES.get('profileimg')
        bday = datetime.datetime.strptime(request.POST['bday'], '%d-%m-%Y').strftime('%Y-%m-%d') if request.POST.get('bday') else datetime.date.today()
        address = request.POST['address']
        country = request.POST['country']
        pincode = request.POST['pincode']
        phonenumber = request.POST['phonenumber']
        city = request.POST['city']
        position = request.POST['position']
        location = request.POST['location']
        userid = request.POST['userid']
        age = request.POST['age']
        companyname = request.POST['companyname']
        periodfrom = datetime.datetime.strptime(request.POST['periodfrom'], '%d-%m-%Y').strftime('%Y-%m-%d') if request.POST.get('periodfrom') else datetime.date.today()
        periodto =  datetime.datetime.strptime(request.POST['periodto'], '%d-%m-%Y').strftime('%Y-%m-%d') if request.POST.get('periodto') else datetime.date.today()
       
        account_model.firstname = firstname
        account_model.lastname = lastname
        account_model.gender = gender
        account_model.bday = bday
        account_model.address = address
        account_model.country = country
        account_model.pincode = pincode
        account_model.phonenumber = phonenumber
        account_model.city = city
        account_model.position = position
        account_model.location = location
        account_model.companyname = companyname
        account_model.periodfrom = periodfrom
        account_model.periodto = periodto
        account_model.userid = userid
        account_model.age = age
        account_model.profileimg = profileimg
        account_model.save()
    

        return redirect(reverse('account:profile'))
    

    context = {
        'account_model':account_model,
        'user_model':user_model
    }

    return render(request, 'accountsetting/edit_profile.html',context)

def change_password(request):
    user_model = Account.objects.filter(user=request.user).first()
    if request.method == 'POST':
        
        old_password = request.POST.get('oldpass')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        user = request.user
        
   
        if user.check_password(old_password):
            if password1 == password2:
                
                user.set_password(password1)
                user.save()
                update_session_auth_hash(request, user)
                
                messages.success(request, 'Successfully changed your password')
                return redirect(reverse('account:change_password'))
            else:
                messages.error(request, 'Passwords do not match')
        else:
            messages.error(request, 'Old password is incorrect')
    
    
    return render(request, 'accountsetting/change_password.html',{'user_model':user_model}) 


