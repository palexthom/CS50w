import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.views.generic import ListView

from .models import User, Post


class PostList(ListView):
    paginate_by = 10
    model = Post


def index(request):
    return posts(request)


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
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


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
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


@csrf_exempt
@login_required
def compose(request):
    # Composing a new post
    print("Composing a new Post")
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    # Check content
    data = json.loads(request.body)
    print(f"data : {data}")
    if data.get("body") == "":
        return JsonResponse({
            "error": "Post should contain at leas a character."
        }, status=400)

    body = data.get("body", "")
    print(f"body: {body}")
    print(f"user: {request.user}")
    print(f"username: {request.user.username}")

    post = Post(
        author=request.user,
        body=body,
    )

    post.save()
    return JsonResponse({"message": "Post sent successfully."}, status=201)


def posts(request):
    print("Views : entering posts")
    print("Views : getting all posts")
    posts = Post.objects.all()

    # else that's an error
    if len(posts) == 0:
        print("Je passe dans l'erreur")
        return JsonResponse({"error": "No posts to display."}, status=400)

    # Order posts
    print("Let's order posts")
    posts = posts.order_by("-timestamp").all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    print("Let's render homepage")
    return render(request, "network/index.html", {'page_obj': page_obj})


def following(request):
    print("Following : entering posts")

    # User whose Posts we want
    current_user = User.objects.get(username=request.user.username)
    # List of people he's following
    usr_list = current_user.following.all()

    print(current_user)
    print(usr_list)

    # Get posts
    posts = Post.objects.filter(author__in=usr_list)

    # check if we have any
    if len(posts) == 0:
        print("Je passe dans l'erreur")
        return JsonResponse({"error": "No posts to display."}, status=400)

    # Order posts
    print("Let's order posts")
    posts = posts.order_by("-timestamp").all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    print("Let's render homepage")
    return render(request, "network/index.html", {'page_obj': page_obj})


def usernamelist():
    users = User.objects.all()
    usernames = []
    for user in users:
        usernames.append(user.username)
    return usernames


def user(request, user_name):
    try:
        user = User.objects.get(username=user_name)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found."}, status=404)

    if request.method == "GET":
        usernames = usernamelist()
        # If user_id is a valid user, display his posts
        if user_name in usernames:
            print(f"Let's get the content from {user_name}")
            posts = Post.objects.filter(author=User.objects.get(username=user_name))
            following = [user.username for user in user.following.all()]
            followers = [user.username for user in user.followers.all()]
            nb_following = len(following)
            nb_followers = len(followers)

        # else that's an error
        else:
            print("Je passe dans l'erreur")
            return JsonResponse({"error": "Invalid user."}, status=400)

        # Order posts
        print("Let's order posts")
        posts = posts.order_by("-timestamp").all()
        paginator = Paginator(posts, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        print("Let's render userpage")
        return render(request, "network/index.html", {
            'page_obj': page_obj,
            "profile_name": user_name,
            "following": nb_following,
            "followers": nb_followers,
            "is_following": request.user.username in followers
        })


def follow(request, username):
    # add username to following list
    print("Je rentre dans follow")
    try:
        # get user object whose username is the parameter
        profile = User.objects.get(username=username)
        user = User.objects.get(username=request.user)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found."}, status=404)

    print(profile)
    print(user)
    user.following.add(profile)
    user.save()

    return redirect('user', username)


def unfollow(request, username):
    # remove username from following list
    print("Je rentre dans unfollow")
    try:
        # get user object whose username is the parameter
        profile = User.objects.get(username=username)
        user = User.objects.get(username=request.user)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found."}, status=404)

    print(profile)
    print(user)
    user.following.remove(profile)
    user.save()

    return redirect('user', username)
