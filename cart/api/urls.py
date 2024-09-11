from django.urls import path

from . import views

urlpatterns = [
    path('add/', views.AddToCart.as_view(), name='add-to-cart'),
    path('remove/<int:pk>/', views.RemoveFromCart.as_view(), name='remove-fro-cart'),
    path('view/', views.ViewCart.as_view(), name='view-cart'),
    path('increase/decrease-qty/<int:pk>/', views.IncreaseDecreaseQty.as_view(), name='increase-qty'),
    path('order/', views.OrderListCreateAPIView.as_view(), name='create-order'),
    path('order_Details/<int:pk>/', views.ViewOrderDetails.as_view(), name='order-details'),
]
