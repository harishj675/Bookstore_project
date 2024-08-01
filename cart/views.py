from bookstore.models import Book
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render, reverse
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
        return JsonResponse({'success': True})
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
        return JsonResponse({'success': True})


def remove_from_cart(request, cart_id):
    try:
        book_cart_item = UserCart.objects.get(pk=cart_id)
        book_cart_item.delete()
    except UserCart.DoesNotExist:
        return HttpResponseNotFound("Cart item not found.")

    return HttpResponseRedirect(reverse('cart:cart'))


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
    print('order created successfully...')
    return HttpResponse('<h1>Order created successfully....</h1>')


def view_orders(request):
    orders_list = Order.objects.all()
    print('order list method called....')
    return render(request, 'staff/view_orders.html', {'orders_list': orders_list})


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


def update_order_status(request, order_id):
    order = Order.objects.get(pk=order_id)
    status = request.POST['order_status']
    order.order_status = status
    order.save()
    return HttpResponseRedirect(reverse('cart:view_all_orders'))
