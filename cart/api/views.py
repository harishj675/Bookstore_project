from bookstore.models import Book
from django.contrib.auth.models import User
from django.db.models import Sum, F
from django.shortcuts import get_object_or_404
from django.shortcuts import reverse
from rest_framework import generics
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import UserProfile, Notifications

from .serializers import CartViewSerializer, OrderSerializer
from ..models import Cart as UserCart, Order, OrderItems
from ..views import calculate_discount


class CheckCart(APIView):
    def get(self, request):
        return Response(
            {
                "message": "Cart API Endpoints working fine"
            }
        )


class AddToCart(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            quantity = int(request.GET.get('quantity', 1))
            book = get_object_or_404(Book, pk=pk)
            cart_item = UserCart.objects.filter(book_id=pk, user=self.request.user).first()

            if cart_item:
                cart_item.quantity += quantity
                cart_item.total_price_original = book.price * cart_item.quantity
                cart_item.discounted_price = calculate_discount(cart_item.total_price_original, book.discount)
                cart_item.save()
            else:
                UserCart.objects.create(
                    user=request.user,
                    book=book,
                    quantity=quantity,
                    total_price_original=book.price * quantity,
                    discounted_price=calculate_discount(book.price * quantity, book.discount)
                )

            return Response({'success': True, "message": "Book added successfully to cart"},
                            status=status.HTTP_200_OK)

        except ObjectDoesNotExist as e:
            print("Error in  addding book to the cart :::", e)
            return Response({'success': False, "message": str(e)},
                            status=status.HTTP_404_NOT_FOUND)

        except ValueError as e:
            return Response({'success': False, "message": "Invalid quantity provided"},
                            status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'success': False, "message": f"An error occurred: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RemoveFromCart(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, cart_id):
        try:
            book_cart_item = UserCart.objects.get(pk=cart_id)
            book_cart_item.delete()
            return Response({
                "message": "Book removed from cart"
            }, status=status.HTTP_200_OK)
        except Exception as e:
            print("Error in remove book form the cart :::", e)
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


class IncreaseQty(APIView):
    def get(self, request, cart_id):
        try:
            book_cart_item = get_object_or_404(UserCart, pk=cart_id)
            if book_cart_item:
                book = get_object_or_404(Book, pk=book_cart_item.book_id)
                if book_cart_item.quantity < book.quantity:
                    book_cart_item.quantity = book_cart_item.quantity + 1
                    book_cart_item.total_price_original = book.price * book_cart_item.quantity
                    book_cart_item.discounted_price = calculate_discount(book_cart_item.total_price_original,
                                                                         book.discount)
                    book_cart_item.save()
                    return Response({"message": "Qty Increased successfully."}, status=status.HTTP_200_OK)
                else:
                    return Response({"error": "Insufficient stock available."}, status=status.HTTP_400_BAD_REQUEST)
        except UserCart.DoesNotExist:
            return Response({"error": "Cart item not found."}, status=status.HTTP_404_NOT_FOUND)
        except Book.DoesNotExist:
            return Response({"error": "Book not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": "Internal Server Error", "details": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DecreaseQty(APIView):
    def get(self, request, cart_id):
        try:
            book_cart_item = get_object_or_404(UserCart, pk=cart_id)

            if book_cart_item.quantity <= 1:
                return Response({"error": "Quantity cannot be decreased further."},
                                status=status.HTTP_400_BAD_REQUEST)

            try:
                book = get_object_or_404(Book, pk=book_cart_item.book_id)
            except ObjectDoesNotExist:
                return Response({"error": "Book not found."}, status=status.HTTP_404_NOT_FOUND)

            book_cart_item.quantity -= 1
            book_cart_item.total_price_original = book.price * book_cart_item.quantity

            try:
                book_cart_item.discounted_price = calculate_discount(book_cart_item.total_price_original,
                                                                     book.discount)
            except Exception as e:
                return Response({"error": f"Failed to calculate discount: {str(e)}"},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            book_cart_item.save()

            return Response({"message": "Quantity decreased successfully."}, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response({"error": "Cart item not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"An unexpected error occurred: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CreateOrderAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        cart_list = UserCart.objects.filter(user_id=user.id)
        total_discounted_price = UserCart.objects.aggregate(discount=Sum(F('discounted_price')))['discount'] or 0

        # Create the order
        order = Order.objects.create(
            order_total_amount=total_discounted_price,
            user=user,
            numbers_of_items=len(cart_list)
        )

        for item in cart_list:
            OrderItems.objects.create(
                order=order,
                book=Book.objects.get(pk=item.book_id),
                quantity=item.quantity,
            )
            item.delete()

        staff = UserProfile.objects.get(roll='Staff')
        user_staff = User.objects.get(id=staff.user_id)
        Notifications.objects.create(
            user=user_staff,
            message=f'New order created by {user.first_name}',
            url=reverse('cart:view_order_details', args=[order.id])
        )

        serializer = OrderSerializer(order)
        return Response(
            {
                "message": "Order created successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)


class ViewOrder(generics.ListAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class ViewOrderDetails(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
