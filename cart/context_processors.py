# In your view or context processor
from .models import Cart


def get_cart_count(request):
    cart_products = Cart.objects.filter(user_id=request.user.id)
    cart_count = len(cart_products)
    return {'cart_count': cart_count}
