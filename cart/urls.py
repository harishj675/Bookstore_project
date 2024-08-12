from django.urls import path

from . import views

app_name = 'cart'
urlpatterns = [
    path('', views.ViewCart.as_view(), name='cart'),
    path('<int:book_id>/add/', views.add_to_cart, name='add_to_cart'),
    path('<int:cart_id>/remove/', views.remove_from_cart, name='remove_from_cart'),
    path('<int:cart_id>/increase', views.increase_qty, name='increase_qty'),
    path('<int:cart_id>/decrease', views.decrease_qty, name='decrease_qty'),
    path('create_order/', views.create_order, name='create_order'),
    path('<int:order_id>/cancel_order/', views.cancel_order, name='cancel_order'),

    # staff urls
    path('staff/view_order', views.view_orders, name='view_all_orders'),
    path('staff/<int:pk>/view_order_details', views.ViewOrderDetails.as_view(),
         name='view_order_details'),
    path('staff/<int:order_id>/update_order_status', views.update_order_status, name='update_order_status'),
    path('staff/change_order_status ', views.change_order_status, name='change_order_status'),
    path('staff/completed_orders_list', views.completed_orders_list, name='completed_orders_list'),

]
