from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist

from .models import User, ListingManager, Listing, Comment, Bid
from .helpers import highest_bid, highest_bidder
from datetime import datetime


def index(request):
    # retrieve all open listings
    listings = Listing.objects.filter(status='O')
    print(listings)
    # retrieve current highest bid
    listings_with_bids = []
    for listing in listings:
        listings_with_bids.append((listing,highest_bid(listing)))

    print(listings_with_bids)

    return render(request, "auctions/index.html", {
        "listings": listings_with_bids
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
        try:
            listing = Listing.objects.get(id=listing_id)
        except ObjectDoesNotExist:
            message = "Sorry, there is no listing matching your query."
            return apology(request,
                           message,
                           "Would you like to see ",
                           "open listings",
                           "index")

        comments = Comment.objects.filter(listing_id=listing_id)
        is_open = listing.status == 'O'
        is_buyer = False

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

            # if listing closed, check if user is buyer
            if not is_open:
                is_buyer = listing.won_bid == request.user.username

        else:
            # if user not authenticated, he's no buyer, watching, author
            print("On passe ici")
            is_watched = False
            is_author = False
            is_buyer = False

        # we show closed listings only to authors and buyers
        # we show open listings to anyone
        print(f'open:{is_open};author:{is_author};buyer:{is_buyer}')
        if (not is_open and (is_author or is_buyer)) or is_open:
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "comments": comments,
                "author": is_author,
                "watched": is_watched,
                "open": is_open,
                "highest_bid": highest_bid(listing),
                "highest_bidder": highest_bidder(listing)
            })
        else:
            message = "Sorry, we're showing closed listings only to the person who sold it or bought it."
            return apology(request,
                           message,
                           "Would you like to see ",
                           "open listings",
                           "index")


def category(request, category):
    if request.method == "GET":
        for cat in Listing.CAT_BIKE:
            if cat[0] == category:
                name_cat = cat[1]

        return render(request, "auctions/category.html", {
            "category": name_cat,
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
    listing.won_bid = highest_bidder(listing)
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
    try:
        bid_placed = int(request.POST['bid_placed'])
    except ValueError:
        return apology(request, "You didn't enter an integer value.",
                       "Do you want to go back to ",
                       "listing page",
                       f'{request.POST["from"]}')

    if bid_placed > highest_bid:
        # save that bid
        print("Bid Saved")
        Bid.objects.create_bid(bid_placed, listing_id, request.user.username)
    else:
        print("Bid not saved")
        return apology(request, "Sorry your bid isn't high enough.",
                       "Do you want to go back to ",
                       "listing page",
                       f'{request.POST["from"]}')

    # reload page
    return redirect('listing', listing_id)


def apology(request, top, bottom, link_msg, url):
    return render(request, 'auctions/apology.html', {
        "top": top,
        "bottom": bottom,
        "link_msg": link_msg,
        "url_name": url
    })


def categories(request):
    return render(request, "auctions/categories.html", {
        "categories": Listing.CAT_BIKE
    })


def my_items(request):
    username = request.user.username
    listings_sold = Listing.objects.filter(username=username, status='C')
    listings_bought = Listing.objects.filter(won_bid=username)

    listings_sold_with_bids = []

    for listing in listings_sold:
        listings_sold_with_bids.append((listing, highest_bid(listing)))

    listings_bought_with_bids = []
    for listing in listings_bought:
        listings_bought_with_bids.append((listing, highest_bid(listing)))

    return render(request, "auctions/myitems.html", {
        "listings_sold": listings_sold_with_bids,
        "listings_bought": listings_bought_with_bids
    })
