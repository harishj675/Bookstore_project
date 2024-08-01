from django.contrib import admin

from .models import Book, BookSpecifications, Rating, StockLevel

# Register your models here.

admin.site.register(Book)
admin.site.register(BookSpecifications)
admin.site.register(Rating)
admin.site.register(StockLevel)
