from bookstore.models import Book
from rest_framework import serializers

from ..models import Cart as UserCart, Order, OrderItems


class BookViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['title', 'author', 'price', 'discount']


class CartViewSerializer(serializers.ModelSerializer):
    book = BookViewSerializer()

    class Meta:
        model = UserCart
        fields = ['id', 'book', 'user', 'quantity', 'total_price_original', 'discounted_price']


class OrderItemSerializer(serializers.ModelSerializer):
    book_title = serializers.SerializerMethodField()

    class Meta:
        model = OrderItems
        fields = ['book', 'book_title', 'quantity']

    def get_book_title(self, obj):
        return obj.book.title


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(source='orderitems_set', many=True)

    class Meta:
        model = Order
        fields = ['id', 'order_total_amount', 'numbers_of_items', 'items', 'order_status']
