from django.urls import path

from . import views

app_name = 'cart'
urlpatterns = [
    path('', views.view_cart, name='cart'),
    path('<int:book_id>/add/', views.add_to_cart, name='add_to_cart'),
    path('<int:cart_id>/remove/', views.remove_from_cart, name='remove_from_cart'),
    path('<int:cart_id>/increase', views.increase_qty, name='increase_qty'),
    path('<int:cart_id>/decrease', views.decrease_qty, name='decrease_qty'),

]
