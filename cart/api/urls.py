from django.urls import path

from . import views

urlpatterns = [
    path('', views.CheckCart.as_view()),
    path('add/<int:pk>/', views.AddToCart.as_view(), name='add-to-cart'),
    path('remove/<int:cart_id>/', views.RemoveFromCart.as_view(), name='remove-fro-cart'),
    path('view/', views.ViewCart.as_view(), name='view-cart'),
    path('increase-qty/<int:cart_id>/', views.IncreaseQty.as_view(), name='increase-qty'),
    path('decrease-qty/<int:cart_id>/', views.DecreaseQty.as_view(), name='increase-qty'),
    path('create-order/', views.CreateOrderAPIView.as_view(), name='create-order'),
    path('view-order/', views.ViewOrder.as_view(), name='view-order'),
    path('order-details/<int:pk>/', views.ViewOrderDetails.as_view(), name='order-details')
]
