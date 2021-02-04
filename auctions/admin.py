from django.contrib import admin
from .models import User, Listing, ListingManager, Comment, CommentManager, Bid


class ListingAdmin(admin.ModelAdmin):
    list_display = ("title", "brand", "category", "username", "start_bid", "status", "won_bid", )


class BidAdmin(admin.ModelAdmin):
    list_display = ("listing_id","username", "bid_val")


# Register your models here.
admin.site.register(User)
admin.site.register(Listing, ListingAdmin)
admin.site.register(Comment)
admin.site.register(Bid, BidAdmin)

