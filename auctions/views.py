from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import Listing, Bid, Comment, Watchlist, Comment
from django import forms
from .models import User


def index(request):
    return render(request, "auctions/index.html", {
        "listing": Listing.objects.all(),
        "bid": Bid.objects.all()
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required
def create(request):
    if request.method == "POST":
        listing = Listing()
        bid = Bid()
        form = createListing(request.POST)
        if form.is_valid():
            listing.owner = request.user.username
            listing.title = form.cleaned_data['title']
            listing.starting_bid = form.cleaned_data['bid']
            listing.description = form.cleaned_data['descr']
            listing.url = form.cleaned_data['url']
            listing.category = form.cleaned_data['category']
            bid.user = request.user.username
            bid.bid = form.cleaned_data['bid']
            bid.save()
            listing.bids = bid
            listing.save()

    return render(request, "auctions/create.html", {
        "form": createListing()
    })


def categories(request):
    return render(request, "auctions/categories.html", {
        "categories": cat_choices
    })


def category(request, title):
    return render(request, "auctions/category.html", {
        "title": title,
        "listing": Listing.objects.all()
    })


class bidForm(forms.Form):
    new_bid = forms.DecimalField(label="bid")


class commentForm(forms.Form):
    comments = forms.CharField(label="comment", widget=forms.Textarea())


def listing(request, title):
    if request.method == "POST":
        if "remove" in request.POST:
            Watchlist.objects.all().filter(user=request.user.username,
                                           listing=Listing.objects.all().filter(title=title).first()).first().delete()
        elif "add" in request.POST:
            watchlist = Watchlist()
            watchlist.user = request.user.username
            watchlist.listing = Listing.objects.all().filter(title=title).first()
            watchlist.save()

        elif "bid" in request.POST:
            newbid = Bid.objects.all().filter(
                listing=Listing.objects.filter(title=title).first()).first()
            var = Listing.objects.filter(title=title).first()
            bidUpdate = bidForm(request.POST)
            if bidUpdate.is_valid():
                if bidUpdate.cleaned_data['new_bid'] > newbid.bid and bidUpdate.cleaned_data['new_bid'] >= var.starting_bid:
                    newbid.bid = bidUpdate.cleaned_data['new_bid']
                    newbid.user = request.user.username
                    newbid.save()
                else:
                    messages.error(request, 'Bid is too low')
        else:
            formCom = commentForm(request.POST)
            comments = Comment()
            if formCom.is_valid():
                comments.comments = formCom.cleaned_data['comments']
                comments.user = request.user.username
                comments.listing = Listing.objects.all().filter(title=title).first()
                comments.save()

    return render(request, "auctions/listing.html", {
        "title": title,
        "watchlist": Watchlist.objects.all().filter(user=request.user.username, listing=Listing.objects.all().filter(title=title).first()).first(),
        "current": Listing.objects.all().filter(title=title).first(),
        "comment": Comment.objects.all().filter(listing=Listing.objects.all().filter(title=title).first()),
        "bid": bidForm(),
        "formComment": commentForm()
    })


@ login_required
def watchlist(request):

    return render(request, "auctions/watchlist.html", {
        "watchlist": Watchlist.objects.all().filter(user=request.user.username)
    })


cat_choices = (
    ("None", "None"),
    ("Electronics", "Electronics"),
    ("Toy", "Toy"),
    ("Beauty", "Beauty"),
    ("Education", "Education"),
    ("Sports", "Sports"),


)


def close(request, title):
    closeListing = Listing.objects.filter(title=title).first()
    closeListing.status = False
    closeListing.save()
    return HttpResponseRedirect(f"/listing/{title}")


class createListing(forms.Form):
    title = forms.CharField(label="Entry title",
                            widget=forms.TextInput())
    descr = forms.CharField(label="Description",
                            widget=forms.Textarea(),)
    url = forms.URLField(label="Image url", required=False)
    bid = forms.DecimalField(label="Bid")
    category = forms.ChoiceField(choices=cat_choices)
