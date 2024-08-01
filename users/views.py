from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, reverse

from .forms import LoginForm
from .models import UserProfile


def profile(request, user_id):
    return render(request, 'user/profile.html')


def create_user(request):
    pass


def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            print("user authenticate successfully....")
            login(request, user)
            user_profile = UserProfile.objects.get(user_id=user.id)
            if user_profile.roll == 'Staff':
                return HttpResponseRedirect(reverse('users:staff_home'))
            if user_profile.roll == 'Manger':
                return HttpResponseRedirect(reverse('users:staff_home'))

            return HttpResponseRedirect(reverse('book:home'))
        else:
            print("Error in authenticating the user details.")
            return render(request, 'user/login.html', {'login_form': LoginForm()})
    else:
        return render(request, 'user/login.html', {'login_form': LoginForm()})


def logout_user(request):
    logout(request)
    print("user logout successfully...")
    return redirect('book:home')


def update_user(request):
    pass


def staff_home(request):
    return render(request, 'staff/staff.html')


def manger_home(request):
    return render(request, 'user/manger.html')
