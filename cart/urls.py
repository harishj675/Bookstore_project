from django.urls import path

from . import views

app_name = 'cart'
urlpatterns = [
    path('', views.view_cart, name='cart'),
    path('<int:book_id>/add/', views.add_to_cart, name='add_to_cart'),
    path('<int:cart_id>/remove/', views.remove_from_cart, name='remove_from_cart'),
    path('<int:cart_id>/increase', views.increase_qty, name='increase_qty'),
    path('<int:cart_id>/decrease', views.decrease_qty, name='decrease_qty'),
    path('create_order/', views.create_order, name='create_order'),
    path('staff/view_order', views.view_orders, name='view_all_orders'),
    path('staff/<int:order_details_id>/view_order_details', views.view_order_details, name='view_order_details'),
    path('staff/<int:order_id>/update_order_status', views.update_order_status, name='update_order_status')
]
