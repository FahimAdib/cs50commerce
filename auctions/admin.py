from django.contrib import admin
from .models import Comment, Listing, Bid, Watchlist

# Register your models here.
admin.site.register(Watchlist)
admin.site.register(Comment)
admin.site.register(Listing)
admin.site.register(Bid)
