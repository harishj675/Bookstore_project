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


class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'order_total_amount', 'numbers_of_items', 'order_status']


class AddToCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCart
        fields = ['book', 'quantity']

    def create(self, validated_data):
        user = self.context['request'].user
        return UserCart.objects.create(user=user, **validated_data)


class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    order_status = serializers.ChoiceField(choices=Order.STATUS_CHOICES)

    class Meta:
        model = Order
        fields = ['order_status']

    def validate_order_status(self, value):
        if value not in dict(Order.STATUS_CHOICES):
            raise serializers.ValidationError("Invalid status. Choose a valid status from the list.")
        return value
