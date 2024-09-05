from rest_framework import serializers

from ..models import Book, BookSpecifications, Rating, StockLevel


class BookViewAsChild(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'price', ]


class BookListSerializers(serializers.ModelSerializer):
    discounted_price = serializers.IntegerField()

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'price', 'discount', 'quantity', 'genre', 'cover_img', 'discounted_price']


class BookSerializers(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'


class BookSpecificationsSerializers(serializers.ModelSerializer):
    book = BookViewAsChild()

    class Meta:
        model = BookSpecifications
        fields = '__all__'


class BookReviewSerializers(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['book', 'review_title', 'review_text']


class BookReviewViewSerializers(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = '__all__'


class BookCreateSerializers(serializers.ModelSerializer):
    cover_img = serializers.ImageField(required=False)

    class Meta:
        model = Book
        fields = ['title', 'author', 'price', 'discount', 'quantity', 'genre', 'cover_img']


class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockLevel
        fields = '__all__'


class AddStockSerializer(serializers.Serializer):
    book_id = serializers.IntegerField()
    stock_quantity = serializers.IntegerField()
    ACTION_CHOICES = [
        ('add', 'Add'),
        ('remove', 'Remove'),
    ]
    action = serializers.ChoiceField(choices=ACTION_CHOICES)

    def validate(self, data):
        if data['action'] == 'remove' and data['stock_quantity'] < 0:
            raise serializers.ValidationError("Stock quantity cannot be negative when removing stock.")
        return data
