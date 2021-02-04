from .models import Listing, Bid


def highest_bid(listing: Listing):
    # returns highest bid for listing in parameter
    if len(listing.bids.all()) > 0:
        return listing.bids.all()[0].bid_val
    else:
        return 0


def highest_bidder(listing: Listing):
    # returns highest bidder for listing in parameter
    if len(listing.bids.all()) > 0:
        return listing.bids.all()[0].username
    else:
        return "No bid has been made"
