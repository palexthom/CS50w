from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse

from .models import User, ListingManager, Listing, Comment, Bid
from datetime import datetime


def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.filter(status='O')
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
        # Create a listing object
        data_listing = {'title': request.POST["title"],
                        'brand': request.POST["brand"],
                        'description': request.POST["description"],
                        'start_bid': request.POST["start_bid"],
                        'pic_url': request.POST["pic_url"],
                        'cat': request.POST["cat"],
                        'username': 'admin',
                        'status': "open"}

        Listing.objects.create_listing(data_listing)
        return redirect('index')

    else:
        return render(request, "auctions/create.html", {
            "CAT_BIKES": Listing.CAT_BIKE
        })


def listing(request, listing_id):
    if request.method == "POST":

        # when submitting a comment
        listing = Listing.objects.get(id=listing_id)
        Comment.objects.create_comment(request.user.username,
                                       datetime.now(),
                                       request.POST['comment'],
                                       listing)

        return redirect('listing', listing_id)

    else:
        listing = Listing.objects.get(id=listing_id)
        comments = Comment.objects.filter(listing_id=listing_id)

        # If user authenticated
        if request.user.is_authenticated:
            # check if listing belongs to the user
            is_author = listing.username == request.user.username

            # check if listing is in user's watchlist
            user = User.objects.get(username=request.user.username)
            watched_list = user.watchlist.all()

            if listing in watched_list:
                is_watched = True
            else:
                is_watched = False

        else:
            is_watched = False
            is_author = False

        # check if listing is open
        if listing.status == 'O':
            is_open = True
        else:
            is_open = False

        # look for highest bidder
        if len(listing.bids.all()) != 0:
            highest_bidder = listing.bids.all()[0].username
        else:
            highest_bidder = "No bid has been made"

        # if listing not None, we return it to the page
        if listing is not None:
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "comments": comments,
                "author": is_author,
                "watched": is_watched,
                "open": is_open,
                # we configured bids to be returned from highest to lowest
                "highest_bidder": highest_bidder
            })
        else:
            return redirect("index")


def category(request, category):
    if request.method == "GET":
        return render(request, "auctions/category.html", {
            "category": category,
            "listings": Listing.objects.filter(category=category, status='O')
        })


def manage_watchlist(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    user = User.objects.get(username=request.user.username)
    watched_list = user.watchlist.all()

    if listing in watched_list:
        user.watchlist.remove(listing)
    else:
        user.watchlist.add(listing)

    return redirect("watchlist")


def watchlist(request):
    watched = []
    users = User.objects.all()
    uname = request.user.username
    for user in users:
        if uname == user.username:
            watched = user.watchlist.all()

    return render(request, "auctions/watched.html", {
        "listings": watched
    })


def close(request, listing_id):
    # recup l'objet listing, changer son statut à close et son won_bid
    listing = Listing.objects.get(id=listing_id)
    listing.status = 'C'
    listing.won_bid = request.user.username
    listing.save()

    return redirect('index')


def place_bid(request, listing_id):
    # javascript should check if bid is higher than minimum

    # get listing and initial bid
    listing = Listing.objects.get(id=listing_id)
    highest_bid = listing.start_bid

    # get bids for that listing
    bids = Bid.objects.filter(listing_id=listing)

    # look for highest bid
    for bid in bids:
        print(f"{bid.bid_val} // {highest_bid}")
        if bid.bid_val > highest_bid:
            highest_bid = bid.bid_val

    # check if bid placed is higher
    bid_placed = int(request.POST['bid_placed'])
    if bid_placed > highest_bid:
        # save that bid
        print("Bid Saved")
        Bid.objects.create_bid(bid_placed, listing_id, request.user.username)
    else:
        print("Bid not saved")
        return apology(request, "Sorry your bid isn't high enough. Do you want to go back to ",
                       "index",
                       "index")

    # reload page
    return redirect('listing', listing_id)


def apology(request, msg, link_msg, url):
    return render(request, 'auctions/apology.html', {
        "msg": msg,
        "link_msg": link_msg,
        "url_name": url
    })
