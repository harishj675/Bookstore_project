from django.db.models import F, ExpressionWrapper, FloatField, Q
from django.shortcuts import get_object_or_404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, generics, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import UserProfile, Notifications

from .serializers import BookListSerializers, BookSerializers, BookSpecificationsSerializers, BookReviewSerializers, \
    BookReviewViewSerializers, BookCreateSerializers, StockSerializer, AddStockSerializer
from ..models import Book, BookSpecifications, Rating, StockLevel


class BookListViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.annotate(
        discounted_price=ExpressionWrapper(
            F('price') * (1 - F('discount') * 0.01),
            output_field=FloatField()
        )
    )
    serializer_class = BookListSerializers


class SearchBook(APIView):

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='query',
                type=OpenApiTypes.STR,
                description='Search for a book by title or author',
                required=True,
                location=OpenApiParameter.QUERY,
            ),
        ],
        responses={200: 'BookSerializers'},
    )
    def get(self, request):
        query = request.GET.get('query', '')
        query_to_execute = Q(title__icontains=query) | Q(author__icontains=query)
        book_list = Book.objects.filter(query_to_execute).distinct()
        serializer = BookSerializers(book_list, many=True)
        return Response({
            'message': "Query fetched book(s) successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class BookReview(generics.CreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = BookReviewSerializers

    def perform_create(self, serializer):
        try:
            book = serializer.validated_data.get('book')
            serializer.save(user=self.request.user)
            user_profile = UserProfile.objects.get(roll='Staff')
            notify_user = user_profile.user

            notification = Notifications.objects.create(
                user=notify_user,
                message=f'New review added for book {book.title}',
            )
            notification.save()

        except Exception as e:
            print(f"Error in adding review: {e}")
            raise e

    def create(self, request, *args, **kwargs):
        try:

            response = super().create(request, *args, **kwargs)

            return Response({
                "message": "Book review added successfully",
                "data": response.data
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            print(f"Error in creating review: {e}")
            return Response({
                "message": "Internal Server Error",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BookReviewDetails(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = Rating.objects.all()
    serializer_class = BookReviewViewSerializers

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response({
                "message": "Book review deleted successfully."
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "message": "Failed to delete the book review.",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BookSpecificationsListView(generics.ListAPIView):
    serializer_class = BookSpecificationsSerializers

    def get_queryset(self):
        book_id = self.kwargs.get('book_id')
        return BookSpecifications.objects.filter(book_id=book_id)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if queryset.exists():
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                "message": "BookSpecifications fetched successfully.",
                "book_specifications": serializer.data
            }, status=status.HTTP_200_OK)
        return Response({"message": "Book not found"}, status=status.HTTP_404_NOT_FOUND)


class CreateBook(generics.CreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Book.objects.all()
    serializer_class = BookCreateSerializers

    def perform_create(self, serializer):
        book = serializer.save()
        stock_leval = StockLevel.objects.create(
            book=book,
            stock_quantity=book.quantity,
            remaining_quantity=book.quantity,
        )
        stock_leval.save()

        return Response({
            'message': "Book Added successfully..",
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)


class StockLevelList(generics.ListCreateAPIView):
    queryset = StockLevel.objects.all()
    serializer_class = StockSerializer


class AddStock(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=AddStockSerializer,
        responses={200: AddStockSerializer}
    )
    def post(self, request, *args, **kwargs):
        serializer = AddStockSerializer(data=request.data)

        if serializer.is_valid():
            book_id = serializer.validated_data['book_id']
            new_stock_quantity = serializer.validated_data['stock_quantity']

            # Retrieve the stock object for the given book_id
            stock = get_object_or_404(StockLevel, book_id=book_id)

            # Update the stock quantities
            stock.stock_quantity += new_stock_quantity
            stock.remaining_quantity += new_stock_quantity
            stock.save()

            return Response({'success': True}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RemoveStock(APIView):
    @extend_schema(
        request=AddStockSerializer,
        responses={200: AddStockSerializer}
    )
    def post(self, request, *args, **kwargs):
        data = request.data
        new_stock_quantity = int(data.get('stock_quantity', 0))
        book_id = int(data.get('book_id', 0))

        stock = get_object_or_404(StockLevel, book_id=book_id)

        if stock.stock_quantity >= new_stock_quantity:
            stock.stock_quantity -= new_stock_quantity
            stock.remaining_quantity -= new_stock_quantity
            stock.save()
            return Response({'success': True}, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'error': 'Not enough stock to remove the specified quantity.'
            }, status=status.HTTP_400_BAD_REQUEST)
