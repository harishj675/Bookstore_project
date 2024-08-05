from bookstore.models import Book
from cart.models import Order
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, reverse

from .forms import LoginForm, UserProfileForm, SignUpForm
from .models import UserProfile


def calculate_discount(price, discount):
    try:
        price = float(price)
        discount = float(discount)
        discounted_price = price - (price * (discount / 100))
        return round(discounted_price, 2)
    except (ValueError, TypeError):
        return price


def profile(request):
    user_profile = UserProfile.objects.get(user_id=request.user.id)
    try:
        orders = Order.objects.prefetch_related('orderitems_set') \
            .filter(user_id=request.user.id) \
            .order_by('order_date')

    except Exception as e:
        orders = []

    order_list = []
    for order in orders:
        print("called")
        order_dict = {}
        order_dict['order_id'] = order.id
        items_list = []
        for item in order.orderitems_set.all():
            item_dict = {}
            book = Book.objects.get(pk=item.book_id)
            item_dict['item_id'] = item.id
            item_dict['book_title'] = book.title
            item_dict['cover_img'] = book.cover_img
            item_dict['book_author'] = book.author
            item_dict['item_quantity'] = item.quantity
            item_dict['book_price'] = book.price
            item_dict['book_discount'] = book.discount
            item_dict['discounted_price'] = calculate_discount(book.price, book.discount)
            item_dict['total_price'] = item_dict['discounted_price'] * item.quantity
            items_list.append(item_dict)
        order_dict['items'] = items_list
        order_dict['status'] = order.order_status
        order_dict['order_total_amount'] = order.order_total_amount
        order_list.append(order_dict)

    print(len(order_list))
    context = {
        'user_profile': user_profile,
        'order_list': order_list,
    }
    return render(request, 'user/profile.html', context)


def create_user(request):
    if request.method == 'POST':
        try:
            form = SignUpForm(request.POST)
            if form.is_valid():
                user = form.save()
                login(request, user)
                messages.success(request, 'user created successfully and logged..')
                return redirect('book:home')
        except Exception as e:
            print(f'Error in creating user {e}')
            messages.error('Error in creating user')
    else:
        form = SignUpForm()
        return render(request, 'user/user_registration.html', {'form': form})


def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            print("user authenticate successfully....")
            login(request, user)
            messages.success(request, 'you logged successfully...')
            user_profile = UserProfile.objects.get(user_id=request.user.id)
            if user_profile.roll == 'Staff':
                return HttpResponseRedirect(reverse('users:staff_home'))
            if user_profile.roll == 'Manger':
                return HttpResponseRedirect(reverse('users:staff_home'))

            return HttpResponseRedirect(reverse('book:home'))
        else:
            messages.error(request, 'Invalid username / password')
            print("Error in authenticating the user details.")
            return render(request, 'user/login.html', {'login_form': LoginForm()})
    else:
        return render(request, 'user/login.html', {'login_form': LoginForm()})


def logout_user(request):
    logout(request)
    print("user logout successfully...")
    messages.success(request, 'user logout successfully...')
    return redirect('book:home')


def update_user(request):
    if request.method == 'POST':
        try:
            first_name = request.POST['first_name']
            last_name = request.POST['last_name']
            email = request.POST['email']
            address = request.POST['address']
            mobile_number = request.POST['mobile_number']
            pincode = request.POST['pincode']
            user = request.user
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.save()
            user_profile = UserProfile.objects.get(user_id=request.user.id)
            user_profile.address = address
            user_profile.mobile_number = mobile_number
            user_profile.pincode = pincode
            user_profile.save()
            messages.success(request, 'user information updated successfully.')
            return redirect('users:profile')
        except Exception as e:
            print('Error in the updating user')
            messages.error(request, 'Something went wrong')
            return redirect('user:profile')
    else:
        user_profile = UserProfile.objects.get(user_id=request.user.id)
        initial_data = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
            'address': user_profile.address,
            'mobile_number': user_profile.mobile_number,
            'pincode': user_profile.pincode
        }
        form = UserProfileForm(initial=initial_data)
        return render(request, 'user/update_user.html', {'form': form})


def staff_home(request):
    return render(request, 'staff/staff.html')


def manger_home(request):
    return render(request, 'staff/staff.html')
