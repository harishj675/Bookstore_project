from django.urls import path

from . import views

app_name = 'book'
urlpatterns = [
    path('', views.index, name='home'),
    path('book/search/', views.book_search, name='search_book'),
    path('book/<int:book_id>/details/', views.book_details, name='details_book'),
    # path('<char:book_categories>/book_category', views.book_categories, name='book_category')

    # staff urls
    path('book/add/', views.book_add, name='add_book'),
    path('book/<int:book_id>/remove/', views.book_remove, name='remove_book'),
    path('book/<int:book_id>/update/', views.book_update, name='update_book'),
    path('staff/view_books/', views.view_book, name='staff_book_view'),
    path('book/<int:book_id>/add_more_info/', views.add_book_more_info, name='add_book_more_info'),
    path('staff/view_stock/', views.view_stock, name='view_stock')
]
