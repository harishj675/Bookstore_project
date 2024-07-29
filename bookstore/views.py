# Create your views here.
from django.shortcuts import render


def index(request):
    return render(request, 'books/index.html', {'books_list': []})


def book_add(request):
    pass


def book_remove(request, book_id):
    pass


def book_update(request, book_id):
    pass


def book_details(request, book_id):
    return render(request, 'bookstore/detail.html', {'book': []})


def book_search(request):
    # book search by author or title
    pass


def book_review(request, book_id):
    pass


def book_categories(request, book_categories):
    pass


# cart
# Create your views here.

def add_to_cart(request, book_id):
    pass


def remove_from_cart(request, book_id):
    pass


def view_cart(request):
    return render(request, 'bookstore/cart.html', {'book_list': []})


# user

# Create your views here.

def profile(request, user_id):
    return render(request, 'bookstore/profile.html')


def create_user(request):
    pass


def login_user(request):
    pass


def logout_user(request):
    pass


def update_user(request):
    pass
