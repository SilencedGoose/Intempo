from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from intempo.forms import UserForm, UserProfileForm



def index(request):
    context_dict = {}
    context_dict[""] = ""

    response = render(request, 'intempo/index.html', context=context_dict)
    return response


def albums(request):
    context_dict = {}
    context_dict[""] = ""

    response = render(request, 'intempo/albums.html', context=context_dict)
    return response


def album_page(request):
    context_dict = {}
    context_dict["name"] = "placeholder album name"
    context_dict["description"] = "placeholder description"
    context_dict["album_cover"] = "0.png"

    response = render(request, 'intempo/album_page.html', context=context_dict)
    return response


def add_album(request):
    context_dict = {}
    context_dict[""] = ""

    response = render(request, 'intempo/add_album.html', context=context_dict)
    return response


def profile(request):
    context_dict = {}
    context_dict["username"] = "placeholder username"
    context_dict["user_id"] = "0"
    context_dict["join_date"] = "11/03/2021"
    context_dict["profile_picture"] = "0.png"

    response = render(request, 'intempo/profile.html', context=context_dict)
    return response


def signup(request):
    context_dict = {}
    context_dict[""] = ""

    response = render(request, 'intempo/signup.html', context=context_dict)
    return response


def login(request):
    context_dict = {}
    context_dict[""] = ""

    response = render(request, 'intempo/login.html', context=context_dict)
    return response


def not_found(request):
    context_dict = {}
    context_dict[""] = ""

    response = render(request, 'intempo/not_found.html', context=context_dict)
    return response



### USER AUTHENTICATION
def signup(request):
    registered = False

    if request.method == "POST":
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()

            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            if "picture" in request.FILES:
                profile.picture = request.FILES["picture"]

            profile.save()
            registered = True
        else:
            print(user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(request, "intempo/signup.html", context = {"user_form": user_form, "profile_form": profile_form, "registered": registered})



def user_login(request):
    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return redirect(reverse("intempo:home"))
            else:
                return HttpResponse("Your account is disabled.")
        else:
            print(f"Invalid login details: {username}, {password}")
            return HttpResponse("Invalid login details supplied.")

    else:
        return render(request, "intempo/login.html")



@login_required
def user_logout(request):
    logout(request)
    return redirect(reverse("intempo:home"))
