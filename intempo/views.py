from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from intempo.models import Album, UserProfile
from django.contrib.auth.models import User
from intempo.forms import UserForm, UserProfileForm, AddAlbumForm, AddReviewForm,AlbumForm




def index(request):
    context_dict = {}
    context_dict[""] = ""

    response = render(request, 'intempo/index.html', context=context_dict)
    return response


def albums(request):
    context_dict = {}
    form = AlbumForm()
    if request.method == 'GET':
        form = AlbumForm(request.GET)
        
        if form.is_valid():
            if form.cleaned_data['sort'] in [f.name for f in Album._meta.fields[1:4:]]:
                album = Album.objects.order_by(form.cleaned_data['sort'])
            else:
                album = sorted(Album.objects.all(), key=lambda a:a.avg_rating, reverse=True)
            filteredalbum = []
            user_tags = form.cleaned_data['filter'].split(',')
            user_tags = [i.strip().upper() for i in user_tags]
            if user_tags != ['']:
                for A in album:
                    if(set(user_tags).issubset(A.tags_as_list)):
                        filteredalbum.append(A)
            else:
                filteredalbum = album
            
            
            context_dict["Albums"] = filteredalbum
            context_dict["form"] = form
            return render(request, 'intempo/albums.html', context=context_dict)
    
    album = Album.objects.all()
    context_dict["Albums"] = album
    context_dict["form"] = form
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
    form = AddAlbumForm()
    if request.method == 'POST':
        form = AddAlbumForm(request.POST, request.FILES)

        if form.is_valid():

            Album = form.save(commit=False)
            Album.album_cover = request.FILES['album_cover']
            Album.save()
            return redirect(reverse("intempo:albums"))
        else:
            print(form.errors)
            
    context_dict = {}
    context_dict["form"] = form

    response = render(request, 'intempo/add_album.html', context=context_dict)
    return response

def add_review(request):

    #album must be defined
    form = AddReviewForm()
    if request.method == 'POST':

        form = AddReviewForm(request.POST)

        if form.is_valid():
            Review = form.save(commit=False)

            Review.album = album
            Review.user = UserProfile.objects.all().get(user=request.user)
            Review.save()
            return redirect(reverse("intempo:home"))
        else:
            print(form.errors)
    return render(request, "intempo/add_review.html", {"form": form})


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

    response = render(request, '404.html', context=context_dict)
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
