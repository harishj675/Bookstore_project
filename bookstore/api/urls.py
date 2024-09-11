from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'books', views.BookListViewSet)
router.register(r'stock/levels', views.StockLevelViewSet)

urlpatterns = [
    path('search/', views.SearchBook.as_view(), name='book-search'),
    # path('book-review/', views.BookReview.as_view(), name="add-review"),
    # path('book-review/<int:pk>/', views.BookReviewDetails.as_view(), name='book-review'),
    path('', include(router.urls)),
]
