from bookstore.models import Book
from bookstore.models import StockLevel
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render, reverse, redirect
from users.models import Notifications
from users.models import UserProfile

from .models import Cart as UserCart, Order, OrderItems


def calculate_discount(price, discount):
    try:
        price = float(price)
        discount = float(discount)
        discounted_price = price - (price * (discount / 100))
        return round(discounted_price, 2)
    except (ValueError, TypeError):
        return price


@login_required
def add_to_cart(request, book_id):
    quantity = int(request.GET.get('quantity', 1))
    cart_item = UserCart.objects.filter(book_id=book_id)
    if cart_item:
        book = get_object_or_404(Book, pk=book_id)
        cart_book = cart_item[0]
        cart_book.quantity = cart_book.quantity + quantity
        cart_book.total_price_original = cart_book.total_price_original * cart_book.quantity
        cart_book.discounted_price = calculate_discount(cart_book.total_price_original, book.discount)
        cart_book.save()
        if request.GET.get('quantity'):
            return JsonResponse({'success': True})
        else:
            messages.success(request, 'book added successfully in Cart')
            return HttpResponseRedirect(reverse('book:home'))

    else:
        print("Book_id in add to book__", book_id)
        book = get_object_or_404(Book, pk=book_id)
        user = get_object_or_404(User, pk=request.user.id)
        cart = UserCart.objects.create(
            user=user,
            book=book,
            quantity=quantity,
            total_price_original=book.price,
            discounted_price=calculate_discount(book.price, book.discount)
        )
        cart.save()
        if request.GET.get('quantity'):
            return JsonResponse({'success': True})
        else:
            messages.success(request, 'book added successfully in Cart')
            return HttpResponseRedirect(reverse('book:home'))


@login_required
def remove_from_cart(request, cart_id):
    try:
        book_cart_item = UserCart.objects.get(pk=cart_id)
        book_cart_item.delete()
        messages.success(request, 'book removed by cart')
    except UserCart.DoesNotExist:
        messages.error(request, 'cart item not found ')
        print('error in removing book form a cart')

    return HttpResponseRedirect(reverse('cart:cart'))


@login_required
def view_cart(request):
    cart_list = UserCart.objects.filter(user_id=request.user.id)
    number_of_books = len(cart_list)
    total_order_price = 0
    discounted_price = 0

    for item in cart_list:
        book = get_object_or_404(Book, pk=item.book_id)
        total_order_price = total_order_price + item.total_price_original
        discounted_price = discounted_price + item.discounted_price

    delivery_charges = calculate_discount(total_order_price, 97)
    total_amount = round(float(discounted_price) + float(delivery_charges), 2)
    context = {
        'total_order_price': total_order_price,
        'discount': round(float(total_order_price) - float(discounted_price), 2),
        'delivery_charges': delivery_charges,
        'total_amount': total_amount,
        'number_of_books': number_of_books,
        'cart_list': cart_list
    }
    return render(request, 'cart/cart.html', context)


def increase_qty(request, cart_id):
    book_cart_item = get_object_or_404(UserCart, pk=cart_id)
    if book_cart_item:
        book = get_object_or_404(Book, pk=book_cart_item.book_id)
        if book_cart_item.quantity < book.quantity:
            book = get_object_or_404(Book, pk=book_cart_item.book_id)
            book_cart_item.quantity = book_cart_item.quantity + 1
            book_cart_item.total_price_original = book.price * book_cart_item.quantity
            book_cart_item.discounted_price = calculate_discount(book_cart_item.total_price_original, book.discount)
            book_cart_item.save()
            return HttpResponseRedirect(reverse('cart:cart'))
        else:
            return HttpResponseRedirect(reverse('cart:cart'))


def decrease_qty(request, cart_id):
    book_cart_item = get_object_or_404(UserCart, pk=cart_id)
    if book_cart_item:
        if book_cart_item.quantity > 1:
            book = get_object_or_404(Book, pk=book_cart_item.book_id)
            book_cart_item.quantity = book_cart_item.quantity - 1
            book_cart_item.total_price_original = book.price * book_cart_item.quantity
            book_cart_item.discounted_price = calculate_discount(book_cart_item.total_price_original, book.discount)
            book_cart_item.save()
            return HttpResponseRedirect(reverse('cart:cart'))
        else:
            return HttpResponseRedirect(reverse('cart:cart'))


@login_required
def create_order(request):
    cart_list = UserCart.objects.filter(user_id=request.user.id)
    total_order_amount = 0
    discounted_price = 0

    for item in cart_list:
        total_order_amount = total_order_amount + item.total_price_original
        discounted_price = discounted_price + item.discounted_price

    order = Order.objects.create(
        order_total_amount=discounted_price,
        user=request.user,
        numbers_of_items=len(cart_list)
    )
    order.save()

    for item in cart_list:
        order_item = OrderItems.objects.create(
            order=order,
            book=Book.objects.get(pk=item.book_id),
            quantity=item.quantity,
        )
        order_item.save()
        item.delete()
    # or create notification
    staff = UserProfile.objects.get(roll='Staff')
    user = User.objects.get(id=staff.user_id)
    notification = Notifications.objects.create(
        user=user,
        message=f'new ordered created by the {request.user.first_name}',
        url=reverse('cart:view_order_details', args=[order.id])
    )
    notification.save()
    print('order created successfully...')
    messages.success(request, 'ordered created successfully.')
    return redirect('users:profile')


def view_orders(request):
    user_profile = UserProfile.objects.get(user_id=request.user.id)
    status_filter = request.GET.get('status', '')

    if user_profile.roll == 'Staff':
        orders_queryset = Order.objects.filter(order_status='Pending')
    else:
        if status_filter:
            orders_queryset = Order.objects.filter(order_status=status_filter)
        else:
            orders_queryset = Order.objects.all()

    paginator = Paginator(orders_queryset, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'orders': page_obj,
        'status_filter': status_filter
    }

    return render(request, 'staff/view_orders.html', context)


def cancel_order(request, order_id):
    order = Order.objects.get(pk=order_id)
    order.order_status = 'Cancelled'
    order.save()
    messages.success(request, 'odered cancelled successfully.')
    return redirect('users:profile')


def view_order_details(request, order_details_id):
    order = Order.objects.get(pk=order_details_id)
    order_items_list = OrderItems.objects.filter(order_id=order_details_id)
    order_details_list = []
    for item in order_items_list:
        order_info = {}
        book = Book.objects.get(pk=item.book_id)
        order_info['item_id'] = item.id
        order_info['book_title'] = book.title
        order_info['book_price'] = calculate_discount(book.price, book.discount)
        order_info['quantity'] = item.quantity
        order_info['total_price'] = order_info['book_price'] * item.quantity
        order_details_list.append(order_info)
    # get customer details
    customer = User.objects.get(pk=order.user_id)
    customer_profile = UserProfile.objects.get(user_id=order.user_id)
    context = {
        'order_details_list': order_details_list,
        'order': order,
        'total_amount': order.order_total_amount,
        'customer': customer,
        'customer_profile': customer_profile
    }

    return render(request, 'staff/order_details.html', context)


@permission_required('cart.change_order', raise_exception=True)
def update_order_status(request, order_id):
    order = Order.objects.get(pk=order_id)
    status = request.POST['order_status']
    if status == 'shipped':
        order_items_list = OrderItems.objects.filter(order_id=order_id)
        for item in order_items_list:
            book_stock_level = StockLevel.objects.get(book_id=item.book_id)
            book_stock_level.remaining_quantity = book_stock_level.remaining_quantity - item.quantity
            book_stock_level.sell_quantity = book_stock_level.sell_quantity + item.quantity
            book_stock_level.save()
    order.order_status = status
    order.save()
    # sending notification to the user and manager
    order_user = User.objects.get(pk=order.user_id)
    notification = Notifications.objects.create(
        user=order_user,
        message=f"your order status changes current status is {order.order_status}",
        url=reverse('users:profile')
    )
    notification.save()
    if order.order_status == 'processing':
        user_profile = UserProfile.objects.get(roll="Manager")
        manager_user = User.objects.get(id=user_profile.user_id)
        notification = Notifications.objects.create(
            user=manager_user,
            message=f'new order created by {order_user.first_name}',
            url=reverse('cart:view_order_details', args=[order.id])
        )
        notification.save()
    messages.success(request, 'order status updated successfully.')
    return HttpResponseRedirect(reverse('cart:view_all_orders'))


def completed_orders(request):
    pass


def change_order_status(request):
    orders = Order.objects.exclude(order_status__in=['Pending', 'Cancelled', 'Shipped', 'Delivered'])
    paginator = Paginator(orders, 8)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'staff/change_order_status.html', {'orders_list': page_obj})


def completed_orders_list(request):
    orders_list = Order.objects.filter(order_status='delivered')
    return render(request, 'staff/completed_order_list.html', {'orders_list': orders_list})


def sells_report(request):
    pass
