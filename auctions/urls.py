from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("listing/<int:listing_id>", views.listing, name="listing"),
    path("category/<str:category>", views.category, name="category"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("<int:listing_id>/watchlist", views.manage_watchlist, name="manage_watchlist"),
    path("<int:listing_id>/close", views.close, name="close"),
    path("<int:listing_id>/bid", views.place_bid, name="place_bid"),
    path("apology", views.apology, name="apology"),
    path("categories", views.categories, name="categories"),
    path("myitems", views.my_items, name="my_items")

]
