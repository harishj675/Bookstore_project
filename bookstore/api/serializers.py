from rest_framework import serializers

from ..models import Book, BookSpecifications, Rating, StockLevel


class BookSpecificationsSerializers(serializers.ModelSerializer):
    class Meta:
        model = BookSpecifications
        fields = '__all__'


class BookListSerializers(serializers.ModelSerializer):
    book_specifications = BookSpecificationsSerializers(many=True)
    discounted_price = serializers.IntegerField()

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'price', 'discount', 'quantity', 'genre', 'cover_img', 'discounted_price',
                  'book_specifications']


class BookSerializers(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'


class BookReviewCreateSerializers(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ["review_title", "review_text", "book"]


class BookCreateSerializers(serializers.ModelSerializer):
    cover_img = serializers.ImageField(required=False)

    class Meta:
        model = Book
        fields = ['title', 'author', 'price', 'discount', 'quantity', 'genre', 'cover_img']


class StockSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source="book.title")

    class Meta:
        model = StockLevel
        fields = '__all__'


class AddStockSerializer(serializers.Serializer):
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


class BookDisplaySerializerAsChild(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'author']


class StockLevelDisplaySerializer(serializers.ModelSerializer):
    book = BookDisplaySerializerAsChild()

    class Meta:
        model = StockLevel
        fields = '__all__'


class BookReviewDisplaySerializer(serializers.ModelSerializer):
    review = BookDisplaySerializerAsChild()

    class Meta:
        model = Rating
        fields = '__all__'
