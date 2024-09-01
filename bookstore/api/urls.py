from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'books', views.BookListViewSet)

urlpatterns = [
    path('search/', views.SearchBook.as_view(), name='book-search'),
    path('book-specifications/<int:book_id>/', views.BookSpecificationsListView.as_view(), name='book-specifications'),
    path('book-review/', views.BookReview.as_view(), name="add-review"),
    path('book-review/<int:pk>/', views.BookReviewDetails.as_view(), name='book-review'),
    # path('book-add/', views.CreateBook.as_view(), name='add-book'),
    path('book-stock-levels/', views.StockLevelList.as_view(), name='stock-level'),
    path('book-add-stock/', views.AddStock.as_view(), name='add-stock'),
    path('book-remove-stock/', views.RemoveStock.as_view(), name='remove-stock'),
    path('', include(router.urls)),
]
