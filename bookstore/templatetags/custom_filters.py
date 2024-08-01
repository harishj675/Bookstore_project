from django import template

register = template.Library()


@register.filter
def calculate_discount_price(price, discount):
    try:
        price = float(price)
        discount = float(discount)
        discounted_price = price - (price * (discount / 100))
        return round(discounted_price, 2)
    except (ValueError, TypeError):
        return price
