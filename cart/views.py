from bookstore.models import Book
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render, reverse

from .models import Cart as UserCart


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


