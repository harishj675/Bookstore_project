from bookstore.models import Book
from cart.models import Order
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, reverse

from .forms import LoginForm
from .models import UserProfile


def calculate_discount(price, discount):
    try:
        price = float(price)
        discount = float(discount)
        discounted_price = price - (price * (discount / 100))
        return round(discounted_price, 2)
    except (ValueError, TypeError):
        return price


def profile(request, user_id):
    user_profile = UserProfile.objects.get(user_id=user_id)
    orders = Order.objects.prefetch_related('orderitems_set').all()
    print("orders len", len(orders))
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
