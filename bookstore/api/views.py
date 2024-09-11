from django.db.models import F, ExpressionWrapper, FloatField, Q
from django.shortcuts import get_object_or_404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import generics
from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from users.permissions import IsStaffOrReadOnly, IsStaffUser

from .serializers import BookSerializers, BookCreateSerializers, StockSerializer, \
    AddStockSerializer, StockLevelDisplaySerializer, BookReviewCreateSerializers, BookReviewDisplaySerializer ,BookListSerializers
from ..models import Book, StockLevel, Rating


class BookListViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.annotate(
        discounted_price=ExpressionWrapper(
            F('price') * (1 - F('discount') * 0.01),
            output_field=FloatField()
        )
    )
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PUT']:
            return BookCreateSerializers
        return BookListSerializers

    def perform_create(self, serializer):
        book = serializer.save()
        stock_leval = StockLevel.objects.create(
            book=book,
            stock_quantity=book.quantity,
            remaining_quantity=book.quantity,
        )
        stock_leval.save()
        return Response({
            'message': "Book Added successfully.",
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)

    def create(self, request, *args, **kwargs):
        file_uploaded = request.FILES.get('cover_img')
        if file_uploaded:
            request.data['cover_img'] = file_uploaded

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response({
            'message': "Book Added successfully.",
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)


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


class StockLevelViewSet(viewsets.ModelViewSet):
    queryset = StockLevel.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsStaffUser]
    parser_classes = (MultiPartParser, FormParser)

    lookup_field = 'book_id'

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return AddStockSerializer
        if self.request.method == 'GET':
            return StockLevelDisplaySerializer
        return StockSerializer

    def partial_update(self, request, *args, **kwargs):
        stock = get_object_or_404(StockLevel, book_id=kwargs.get('book_id'))

        serializer = self.get_serializer(stock, data=request.data, partial=True)

        if serializer.is_valid():
            quantity = serializer.validated_data['stock_quantity']
            action = serializer.validated_data['action']

            if action == 'remove' and stock.remaining_quantity < quantity:
                return Response(
                    {
                        "success": False,
                        "message": "Not enough stock to remove the specified quantity."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            if action == 'add':
                stock.stock_quantity += quantity
                stock.remaining_quantity += quantity
            else:
                stock.stock_quantity -= quantity
                stock.remaining_quantity -= quantity

            stock.save()

            return Response({"success": True}, status=status.HTTP_200_OK)

        return Response(
            {"success": False, "message": f"Error: {serializer.errors}"},
            status=status.HTTP_400_BAD_REQUEST
        )

    def get_queryset(self):
        return StockLevel.objects.all()

    http_method_names = ['get', 'patch']


class BookReview(generics.CreateAPIView):
    parser_classes = (MultiPartParser, FormParser)
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = BookReviewCreateSerializers

    def get_serializer(self):
        if self.request.method == 'POST':
            return BookReviewCreateSerializers
        return BookReviewDisplaySerializer

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
    permission_classes = [IsAuthenticated, IsStaffUser]
    parser_classes = (MultiPartParser, FormParser)

    queryset = Rating.objects.all()
    serializer_class = BookReviewDisplaySerializer

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
