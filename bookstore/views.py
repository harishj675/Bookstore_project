# Create your views here.
import json

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from .forms import BookAddForm, BookAddMoreInfo
from .models import Book, BookSpecifications, StockLevel


def index(request):
    try:
        book_list = Book.objects.all()
        context = {
            'book_list': book_list
        }
        return render(request, 'bookstore/home.html', context)

    except Exception as e:
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


def book_review(request, book_id):
    pass


def book_details(request, book_id):
    try:
        book = get_object_or_404(Book, pk=book_id)
        try:
            book_specifications = BookSpecifications.objects.get(book_id=book_id)
        except BookSpecifications.DoesNotExist:
            book_specifications = None

        context = {
            'book': book,
            'book_specifications': book_specifications
        }
        return render(request, 'bookstore/detail.html', context)

    except Exception as e:
        return HttpResponse(f'An error occurred: {e}', status=500)


def book_categories(request, book_categories):
    pass


# staff views
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
            # Adding book specifications
            return HttpResponse('Book created successfully ....')
        except KeyError as e:
            return HttpResponse(f'Missing form field: {e}')
        except Exception as e:
            return HttpResponse(f'An error occurred: {e}')

    else:
        return render(request, 'bookstore/add_book.html', {'form': BookAddForm()})


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
        return HttpResponse('book more details added successfully...')

    else:
        return render(request, 'bookstore/add_more_info.html', {'form': BookAddMoreInfo(), 'book_id': book_id})


def book_remove(request, book_id):
    try:
        book = get_object_or_404(Book, pk=book_id)
        book.delete()
        return HttpResponse('Book deleted successfully.....')
    except Http404:
        print("book not found")
        return HttpResponse('Book not found.')
    except Exception as e:
        return HttpResponse(f'An error occurred: {e}')


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

            return HttpResponse('Book updated successfully ....')
        except KeyError as e:
            print('Error in updating book ', e)
            return HttpResponse(f'Missing form field: {e}')
        except Exception as e:
            print('Error in updating book ', e)
            return HttpResponse(f'An error occurred: {e}')

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
    book_list = Book.objects.all()
    return render(request, 'staff/view_books.html', {'book_list': book_list})


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

    print(book_list)
    return render(request, 'staff/view_stocks.html', {'book_list': book_list})


@csrf_exempt
def add_stock(request):
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


def remove_stock(request):
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
            return JsonResponse({'success': False})
