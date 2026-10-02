from django.contrib import admin
from .models import Cast, Genre, Movie, Review


admin.site.register(Genre)
admin.site.register(Movie)
admin.site.register(Cast)
admin.site.register(Review)
