from bookstore.models import Book
from django.db import transaction
from django.db.models import Sum, F
from django.shortcuts import reverse
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from rest_framework import generics
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.models import UserProfile, Notifications

from .serializers import CartViewSerializer, OrderSerializer, AddToCartSerializer, OrderCreateSerializer, \
    OrderStatusUpdateSerializer
from ..models import Cart as UserCart, Order, OrderItems
from ..views import calculate_discount


class AddToCart(generics.CreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = AddToCartSerializer
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        book = serializer.validated_data['book']
        quantity = serializer.validated_data.get('quantity', 1)

        cart_item, created = UserCart.objects.get_or_create(
            user=self.request.user, book=book,
            defaults={'quantity': quantity}
        )

        if not created:
            cart_item.quantity += quantity

        cart_item.total_price_original = book.price * cart_item.quantity
        cart_item.discounted_price = calculate_discount(cart_item.total_price_original, book.discount)
        cart_item.save()

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_book(self, book_id):
        try:
            return Book.objects.get(pk=book_id)
        except Book.DoesNotExist:
            raise serializers.ValidationError({"message": "Book not found"})


class RemoveFromCart(generics.DestroyAPIView):
    queryset = UserCart.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    def destroy(self, request, *args, **kwargs):
        try:
            response = super().destroy(request, *args, **kwargs)
            return Response({
                "message": "Book removed from cart"
            }, status=status.HTTP_200_OK)
        except Exception as e:
            print("Error in removing book from the cart:", e)
            return Response({
                "message": "Internal Server Error"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ViewCart(generics.ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = CartViewSerializer

    def get_queryset(self):
        return UserCart.objects.filter(user_id=self.request.user.id)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        number_of_books = queryset.count()
        total_order_price = sum(item.total_price_original for item in queryset)
        discounted_price = sum(item.discounted_price for item in queryset)

        delivery_charges = calculate_discount(total_order_price, 97)
        total_amount = round(float(discounted_price) + float(delivery_charges), 2)

        response_data = {
            'total_order_price': total_order_price,
            'discount': round(float(total_order_price) - float(discounted_price), 2),
            'delivery_charges': delivery_charges,
            'total_amount': total_amount,
            'number_of_books': number_of_books,
            'cart_list': CartViewSerializer(queryset, many=True).data
        }
        return Response(response_data, status=status.HTTP_200_OK)


class IncreaseDecreaseQty(generics.GenericAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='action',
                type=str,
                description='Specify "increase" to increase quantity or "decrease" to decrease quantity.',
                enum=['increase', 'decrease'],
                location=OpenApiParameter.QUERY
            )
        ],
        responses={
            200: OpenApiResponse(description="Quantity adjusted successfully"),
            400: OpenApiResponse(description="Bad Request"),
            404: OpenApiResponse(description="Not Found"),
            500: OpenApiResponse(description="Internal Server Error")
        }
    )
    def patch(self, request, *args, **kwargs):
        cart_id = self.kwargs['pk']
        action = request.query_params.get('action')

        if action not in ['increase', 'decrease']:
            return Response({"error": "Invalid action."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            book_cart_item = UserCart.objects.get(pk=cart_id)
            book = Book.objects.get(pk=book_cart_item.book_id)

            if action == 'increase':
                if book_cart_item.quantity < book.quantity:
                    book_cart_item.quantity += 1
                else:
                    return Response({"error": "Insufficient stock available."}, status=status.HTTP_400_BAD_REQUEST)
            elif action == 'decrease':
                if book_cart_item.quantity > 1:
                    book_cart_item.quantity -= 1
                else:
                    return Response({"error": "Quantity cannot be decreased further."},
                                    status=status.HTTP_400_BAD_REQUEST)

            book_cart_item.total_price_original = book.price * book_cart_item.quantity
            book_cart_item.discounted_price = calculate_discount(book_cart_item.total_price_original, book.discount)
            book_cart_item.save()

            return Response({"message": f"Quantity {action}d successfully."}, status=status.HTTP_200_OK)

        except UserCart.DoesNotExist:
            return Response({"error": "Cart item not found."}, status=status.HTTP_404_NOT_FOUND)
        except Book.DoesNotExist:
            return Response({"error": "Book not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": "Internal Server Error", "details": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OrderListCreateAPIView(generics.ListCreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return OrderSerializer
        return OrderCreateSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)

    @transaction.atomic
    def perform_create(self, serializer):
        user = self.request.user
        cart_list = UserCart.objects.filter(user=user)
        total_discounted_price = cart_list.aggregate(discount=Sum(F('discounted_price')))['discount'] or 0

        order = serializer.save(
            order_total_amount=total_discounted_price,
            user=user,
            numbers_of_items=cart_list.count()
        )

        order_items = []
        for item in cart_list:
            try:
                book = Book.objects.get(pk=item.book_id)
                order_items.append(OrderItems(
                    order=order,
                    book=book,
                    quantity=item.quantity
                ))
            except Book.DoesNotExist:
                pass

        if order_items:
            OrderItems.objects.bulk_create(order_items)

        UserCart.objects.filter(user=user).delete()

        staff = UserProfile.objects.get(roll='Staff')
        Notifications.objects.create(
            user=staff.user,
            message=f'New order created by {user.first_name}',
            url=reverse('cart:view_order_details', args=[order.id])
        )

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(
                {
                    "message": "Order created successfully",
                    "data": serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {"error": "Failed to create order", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ViewOrderDetails(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    parser_classes = (MultiPartParser, FormParser)
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ['PATCH']:
            return OrderStatusUpdateSerializer
        return OrderSerializer

    def patch(self, request, *args, **kwargs):
        order = self.get_object()
        serializer = self.get_serializer(order, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Order status updated successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            "message": "Failed to update order status.",
            "details": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response({
                "message": "Order deleted successfully."
            }, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response({
                "message": "Order not found."
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "message": "Failed to delete the order.",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    http_method_names = ['get', 'patch', 'delete']
