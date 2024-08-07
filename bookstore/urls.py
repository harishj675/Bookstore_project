from django.urls import path

from . import views

app_name = 'book'
urlpatterns = [
    path('', views.index, name='home'),
    path('book/search/', views.book_search, name='search_book'),
    path('book/<int:book_id>/details/', views.book_details, name='details_book'),
    path('set_language/', views.set_language, name='set_language'),
    path('<int:book_id>/add_book_review/', views.book_review, name='add_book_review'),

    # staff urls
    path('book/add/', views.book_add, name='add_book'),
    path('book/<int:book_id>/remove/', views.book_remove, name='remove_book'),
    path('book/<int:book_id>/update/', views.book_update, name='update_book'),
    path('staff/view_books/', views.view_book, name='staff_book_view'),
    path('book/<int:book_id>/add_more_info/', views.add_book_more_info, name='add_book_more_info'),
    path('staff/view_stock/', views.view_stock, name='view_stock'),
    path('staff/add_stock/', views.add_stock, name='add_stock'),
    path('staff/remove_stock', views.remove_stock, name='remove_stock'),
    path('staff/apply_discount', views.apply_discount, name='apply_discount'),
    path('remove_book_view/', views.remove_book_view, name='remove_book_view'),
    path('staff/view_review_details', views.view_review_details, name='view_review_details'),
    path('staff/<int:rating_id>/delete_book_review', views.delete_book_review, name='delete_book_review'),
    path('staff/<int:rating_id>/publish_book_review', views.publish_book_review, name='publish_book_review'),
]
