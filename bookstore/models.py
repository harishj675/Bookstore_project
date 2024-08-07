from django.contrib.auth.models import User
from django.db import models


# Create your models here.


class Book(models.Model):
    def __str__(self):
        return self.title

    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.IntegerField(default=0)
    quantity = models.IntegerField()
    genre = models.TextField()
    cover_img = models.ImageField(upload_to='books/images/', blank=True, null=True)


class BookSpecifications(models.Model):
    def __str__(self):
        return self.book_description

    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    book_description = models.TextField(null=True, blank=True)
    book_ISBN_13 = models.BigIntegerField(null=True, blank=True)
    book_language = models.CharField(max_length=50, null=True, blank=True)
    book_binding = models.CharField(max_length=50, null=True, blank=True)
    book_publisher = models.CharField(max_length=200, blank=True)
    book_total_pages = models.IntegerField(null=True, blank=True)
    book_tag = models.CharField(max_length=10, default="", null=True, blank=True)


class StockLevel(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    stock_quantity = models.PositiveIntegerField()
    remaining_quantity = models.IntegerField(default=0)
    sell_quantity = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.book.title} - {self.stock_quantity}'


class Rating(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.DecimalField(null=True, blank=True, default=3, max_digits=10, decimal_places=2)
    review_title = models.CharField()
    review_text = models.TextField()
    is_published = models.BooleanField(default=False, null=True, blank=True)
