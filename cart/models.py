from bookstore.models import Book
from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Cart(models.Model):

    def __str__(self):
        return self.book.title

    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    total_price_original = models.IntegerField()
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2)


class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    def __str__(self):
        return f'Order {self.id} - {self.status}'

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now=True)
    order_total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    numbers_of_items = models.IntegerField(null=True, blank=True)
    order_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')


class OrderItems(models.Model):

    def __str__(self):
        return f'{self.quantity} x {self.book.title}'

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.IntegerField()
