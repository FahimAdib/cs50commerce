from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Bid(models.Model):
    user = models.CharField(max_length=64, blank=True)
    bid = models.DecimalField(decimal_places=2, max_digits=10, null=True)


class Listing(models.Model):
    owner = models.CharField(max_length=64, blank=True)
    title = models.CharField(max_length=64, blank=True)
    status = models.BooleanField(default=True)
    description = models.TextField(max_length=500, blank=True)
    starting_bid = models.DecimalField(
        decimal_places=2, max_digits=10, blank=True, default=1)
    url = models.URLField(blank=True)
    category = models.CharField(max_length=64, blank=True)
    bids = models.ForeignKey(
        Bid, on_delete=models.CASCADE, related_name="listing", default=1)


class Comment(models.Model):
    user = models.CharField(max_length=64)
    comments = models.CharField(max_length=200)
    listing = models.ForeignKey(
        Listing, on_delete=models.SET_NULL, related_name="listingComment", default=1, null=True)


class Watchlist(models.Model):
    user = models.CharField(max_length=64, blank=True)
    listing = models.ForeignKey(
        Listing, on_delete=models.SET_NULL, related_name="listingWatchlist", default=1, null=True)
