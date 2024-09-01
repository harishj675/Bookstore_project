# Create your views here.
import json

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.db.models import F, ExpressionWrapper, FloatField
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.shortcuts import reverse, redirect
from django.utils.translation import activate
from users.models import UserProfile, Notifications, User

from .forms import BookAddForm, BookAddMoreInfo
from .models import Book, BookSpecifications, StockLevel, Rating


def index(request):
    try:
        book_list = Book.objects.annotate(
            discounted_price=ExpressionWrapper(
                F('price') * (1 - F('discount') * 0.01),
                output_field=FloatField()
            )
        )
        context = {
            'book_list': book_list
        }
        return render(request, 'bookstore/home.html', context)

    except Exception as e:
        print('error in ----', e)
        return HttpResponse(f'An error occurred: {e}')


def book_search(request):
    query = request.GET['query']
    books_by_title = Book.objects.filter(title__icontains=query)
    books_by_author = Book.objects.filter(author__icontains=query)
    book_list = []
    book_id_list = []
    for book in books_by_title:
        if book.id in book_id_list:
            continue
        else:
            book_list.append(book)
            book_id_list.append(book.id)
    for book in books_by_author:
        if book.id in book_id_list:
            continue
        else:
            book_list.append(book)
            book_id_list.append(book.id)

    return render(request, 'bookstore/home.html', {'book_list': book_list})


@login_required
def book_review(request, book_id):
    print(request.method)
    print(request.POST)
    if request.method == 'POST':
        print('book_review method called.')
        try:
            title = request.POST['review-title']
            review_content = request.POST['review-content']
            book = get_object_or_404(Book, pk=book_id)
            review = Rating.objects.create(
                review_title=title,
                review_text=review_content,
                book=book,
                user=request.user,
            )
            print("created review details....")
            print(review)
            review.save()
            # creating notification for staff user to
            user_profile = UserProfile.objects.get(roll='Staff')
            notify_user = User.objects.get(pk=user_profile.user_id)
            notification = Notifications.objects.create(
                user=notify_user,
                message=f'New review added for book {book.title}',
                url=reverse('book:view_review_details')
            )
            notification.save()
            messages.success(request, 'book review added successfully..')
            return HttpResponseRedirect(reverse('book:details_book', kwargs={'book_id': book_id}))
        except Exception as e:
            print(f"Error in adding review {e}")
            messages.error(request, 'book review not added')
            return HttpResponseRedirect(reverse('book:details_book', kwargs={'book_id': book_id}))


def view_review_details(request):
    # Fetch reviews that are not published
    ratings_queryset = Rating.objects.prefetch_related('book', 'user').all().values(
        'book__title', 'book__author', 'review_title', 'review_text', 'is_published', 'id',
        'user__first_name', 'user__last_name'
    )

    # Pagination
    paginator = Paginator(ratings_queryset, 5)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'review_list': page_obj,
    }

    return render(request, 'staff/review_details.html', context)


def book_details(request, book_id):
    try:
        book = get_object_or_404(Book, pk=book_id)
        rating_list = Rating.objects.filter(book_id=book_id, is_published=True)

        try:
            # similar_book_list = Book.objects.exclude(id=book_id)
            similar_book_list = Book.objects.exclude(id=book_id).annotate(
                discounted_price=ExpressionWrapper(
                    F('price') * (1 - F('discount') * 0.01),
                    output_field=FloatField()
                ))
            book_specifications = BookSpecifications.objects.get(book_id=book_id)
        except BookSpecifications.DoesNotExist:
            book_specifications = None

        context = {
            'book': book,
            'book_specifications': book_specifications,
            'similar_book_list': similar_book_list[:3],
            'ratings_list': rating_list
        }
        return render(request, 'bookstore/detail.html', context)

    except Exception as e:
        return HttpResponse(f'An error occurred: {e}', status=500)


def book_categories(request, book_categories):
    pass


# staff views
@login_required
@permission_required('bookstore.add_book', raise_exception=True)
def book_add(request):
    if request.method == "POST":
        try:
            title = request.POST['title']
            author = request.POST['author']
            price = request.POST['price']
            discount = request.POST['discount']
            quantity = request.POST['quantity']
            genre = request.POST['genre']

            cover_img = request.FILES['cover_img']

            # Create book and add to book table
            book = Book.objects.create(
                title=title,
                author=author,
                price=price,
                discount=discount,
                quantity=quantity,
                genre=genre,
                cover_img=cover_img
            )
            book.save()
            # create stock leval
            stock_leval = StockLevel.objects.create(
                book=book,
                stock_quantity=book.quantity,
                remaining_quantity=book.quantity,
            )
            stock_leval.save()
            return HttpResponseRedirect(reverse('users:staff_home'))
        except KeyError as e:
            messages.error(request, f'missing filed in form {e}')
            return HttpResponseRedirect(reverse('users:staff_home'))
        except Exception as e:
            messages.error(f'error in adding book')
            return HttpResponseRedirect(reverse('users:staff_home'))

    else:
        return render(request, 'bookstore/add_book.html', {'form': BookAddForm()})


@login_required
@permission_required('bookstore.add_bookspecifications', raise_exception=True)
def add_book_more_info(request, book_id):
    if request.method == 'POST':
        book_description = request.POST['book_description']
        isbn = request.POST['book_ISBN_13']
        language = request.POST['book_language']
        binding = request.POST['book_binding']
        publisher = request.POST['book_publisher']
        pages = request.POST['book_total_pages']
        book_tag = request.POST['book_tag']
        book = Book.objects.get(pk=book_id)
        book_specifications = BookSpecifications.objects.create(
            book=book,
            book_description=book_description,
            book_ISBN_13=isbn,
            book_language=language,
            book_binding=binding,
            book_publisher=publisher,
            book_total_pages=pages,
            book_tag=book_tag
        )
        book_specifications.save()
        messages.success(request, 'book specifications added successfully.')
        return HttpResponseRedirect(reverse('users:staff_home'))

    else:
        return render(request, 'bookstore/add_more_info.html', {'form': BookAddMoreInfo(), 'book_id': book_id})


@login_required
@permission_required('bookstore.delete_book', raise_exception=True)
def book_remove(request, book_id):
    try:
        user_profile = UserProfile.objects.get(user_id=request.user.id)
        book = get_object_or_404(Book, pk=book_id)
        book.delete()
        messages.success(request, 'book deleted successfully..')
        return HttpResponseRedirect(reverse('users:staff_home'))
    except Http404:
        print("book not found")
        messages.error(request, f'book not found')
        return HttpResponseRedirect(reverse('users:staff_home'))
    except Exception as e:
        messages.error(request, 'error in removing book')
        return HttpResponse(f'An error occurred: {e}')


@login_required
@permission_required('bookstore.change_book', raise_exception=True)
def book_update(request, book_id):
    if request.method == 'POST':
        try:
            title = request.POST['title']
            author = request.POST['author']
            price = request.POST['price']
            discount = request.POST['discount']
            quantity = request.POST['quantity']
            genre = request.POST['genre']

            # Get the book instance
            book = get_object_or_404(Book, pk=book_id)

            # Update book fields
            book.title = title
            book.author = author
            book.price = price
            book.discount = discount
            book.quantity = quantity
            book.genre = genre

            # Save the updated book instance
            book.save()
            messages.success(request, 'book updated successfully..')
            return HttpResponseRedirect(reverse('users:staff_home'))
        except KeyError as e:
            print('Error in updating book ', e)
            messages.error(request, f'Missing filed in form {e}')
            return HttpResponseRedirect(reverse('users:staff_home'))
        except Exception as e:
            print('Error in updating book ', e)
            messages.error(request, f'error in updating book..')
            return HttpResponseRedirect(reverse('users:staff_home'))

    else:
        book = get_object_or_404(Book, pk=book_id)
        initial_data = {
            'title': book.title,
            'author': book.author,
            'price': book.price,
            'discount': book.discount,
            'quantity': book.quantity,
            'genre': book.genre,
            'cover_img': book.cover_img
        }
        form = BookAddForm(initial=initial_data)
        return render(request, 'bookstore/update_book.html', {'form': form, 'book_id': book_id})


def view_book(request):
    books = Book.objects.all()
    paginator = Paginator(books, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'staff/view_books.html', {'book_list': page_obj})


def view_stock(request):
    books = Book.objects.prefetch_related('stocklevel_set').all()
    book_list = []

    for b in books:
        book = {}
        book['id'] = b.id
        book['title'] = b.title
        book['book_id'] = b.id
        book['price'] = b.price
        for stock in b.stocklevel_set.all():
            book['stock_quantity'] = stock.stock_quantity
            book['remaining_quantity'] = stock.remaining_quantity
            book['update'] = stock.updated_at
        book_list.append(book)

    paginator = Paginator(book_list, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'staff/view_stocks.html', {'book_list': page_obj})


@permission_required('bookstore.change_stocklevel', raise_exception=True)
def add_stock(request):
    print('add stock request callled.....')
    if request.method == 'POST':
        data = json.loads(request.body)
        print(data)
        new_stock_quantity = int(data['stock_quantity'])
        book_id = int(data['book_id'])
        stock = StockLevel.objects.get(book_id=book_id)
        stock.stock_quantity = stock.stock_quantity + new_stock_quantity
        stock.remaining_quantity = stock.remaining_quantity + new_stock_quantity
        stock.save()
        return JsonResponse({'success': True})


@login_required
@permission_required('bookstore.change_stocklevel', raise_exception=True)
def remove_stock(request):
    print('add stock request called.....')
    if request.method == 'POST':
        data = json.loads(request.body)
        print(data)
        new_stock_quantity = int(data['stock_quantity'])
        book_id = int(data['book_id'])
        stock = StockLevel.objects.get(book_id=book_id)
        if stock.stock_quantity > new_stock_quantity:
            stock.stock_quantity = stock.stock_quantity - new_stock_quantity
            stock.remaining_quantity = stock.remaining_quantity - new_stock_quantity
            stock.save()
            return JsonResponse({'success': True})
        else:
            print("Enter stock more than available stock...")
            return JsonResponse({'success': False})


@login_required
@permission_required('bookstore.delete_book', raise_exception=True)
def remove_book_view(request):
    # Fetch all books
    books_queryset = Book.objects.all()

    # Pagination
    paginator = Paginator(books_queryset, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'book_list': page_obj,
    }

    return render(request, 'staff/remove_book_view.html', context)


@login_required
@permission_required('bookstore.change_book', raise_exception=True)
def apply_discount(request):
    if request.method == 'POST':
        try:
            book_id = request.POST['book_id']
            new_discount = request.POST['discount']
            book = Book.objects.get(pk=book_id)
            book.discount = new_discount
            book.save()
            messages.success(request, f'Discount applied to the book {book.title}')
            return HttpResponseRedirect(reverse('book:apply_discount'))
        except Exception as e:
            messages.error(request, 'Error in applying discount on book')
    else:
        books_queryset = Book.objects.all()
        paginator = Paginator(books_queryset, 10)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        return render(request, 'staff/apply_discount.html', {'book_list': page_obj})


def set_language(request):
    lang_code = request.GET.get('language', settings.LANGUAGE_CODE)
    activate(lang_code)
    response = redirect(request.META.get('HTTP_REFERER', '/'))
    response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code)
    return response


def delete_book_review(request, rating_id):
    try:
        rating = get_object_or_404(Rating, pk=rating_id)
        rating.delete()
        messages.success(request, 'book review deleted successfully.')
        return HttpResponseRedirect(reverse('book:view_review_details'))
    except Exception as e:
        print("Error in deleting book review")
        messages.error(request, 'Error in deleting book.', e)
        return HttpResponseRedirect(reverse('book:view_review_details'))


def publish_book_review(request, rating_id):
    try:
        rating = get_object_or_404(Rating, pk=rating_id)
        rating.is_published = True
        rating.save()
        messages.success(request, 'book review published successfully.')
        return HttpResponseRedirect(reverse('book:view_review_details'))
    except Exception as e:
        print("Error in publishing  book review", e)
        messages.error(request, 'Error in publishing book.')
        return HttpResponseRedirect(reverse('book:view_review_details'))
