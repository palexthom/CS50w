from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path("<str:entree>", views.entry, name="entry"),
    path("search/", views.search, name="search"),
    path("new/", views.new, name="new"),
    path("random/", views.rand_entry, name="random"),
    path("<str:entree>/edit/", views.edit, name="edit")
]
