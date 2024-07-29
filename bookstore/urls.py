from django.urls import path

from . import views

app_name = 'book'
urlpatterns = [
    path('', views.index, name='home'),
    path('add/', views.book_add, name='add_book'),
    path('<int:book_id>/remove/', views.book_remove, name='remove_book'),
    path('<int:book_id>/update/', views.book_update, name='update_book'),
    path('search/', views.book_search, name='search_book'),
    path('<int:book_id>/details/', views.book_details, name='details_book'),
    # path('<char:book_categories>/book_category', views.book_categories, name='book_category')

    # cart
    path('cart/', views.view_cart, name='cart'),
    path('<int:book_id>/add/', views.add_to_cart, name='add_to_cart'),
    path('<int:book_id>/remove/', views.remove_from_cart, name='remove_from_cart'),

    # user
    path('<int:user_id>/profile/', views.profile, name='profile'),
    path('login/', views.login_user, name='login'),
    path('create/', views.create_user, name='create_user'),
    path('logout/', views.logout_user, name='logout'),
    path('update/', views.update_user, name='update_user'),
]
