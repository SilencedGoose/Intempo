from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from intempo.models import Album, UserProfile, Review
from django.contrib.auth.models import User
from intempo.forms import UserForm, UserProfileForm, AddAlbumForm, AddReviewForm, AlbumForm, UpdateUserForm, UpdateUserProfileForm, AddCommentForm
from django.contrib import messages
from django.http import JsonResponse

def get_album_info_as_list(album):
    string = album.name + " " + album.artist + " " + album.description + " " + str(album.creation_date).replace("-", " ")
    list = string.upper().split(" ")
    return list

def index(request):
    context_dict = {
        "trending": Album.trending(),
        "top": Album.top_rated()
    }

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
                    for t in user_tags:
                        if(t in A.tags_as_list):
                            filteredalbum.append(A)
            else:
                filteredalbum = album
                
            search = form.cleaned_data['search']
            if search != '': 
                new_filtered_album = [i for i in filteredalbum]
                filteredalbum = []
                search = search.split(" ")
                
                for A in new_filtered_album:
                    for s in search:
                        if s.upper() in get_album_info_as_list(A):
                            filteredalbum.append(A)
                            break

            context_dict["albums"] = filteredalbum
            context_dict["form"] = form
            return render(request, 'intempo/albums.html', context=context_dict)

    album = Album.objects.all()
    context_dict["Albums"] = album
    context_dict["form"] = form
    response = render(request, 'intempo/albums.html', context=context_dict)
    return response

def album_page(request, album_id):
    try:
        album = Album.objects.get(id=album_id)
    except Album.DoesNotExist:
        return not_found(request)
    
    reviews = Review.for_album(album)
    context_dict = {}
    
    context_dict["album"] = album
    context_dict["reviews"] = reviews
    if request.user.is_anonymous:
        context_dict["rated"] = True
    else:
        user = UserProfile.get_by_username(request.user.username)
        context_dict["rated"] = user.has_rated(album)
    context_dict["add_comment"] = AddCommentForm()
    context_dict["add_review"] = AddReviewForm()

    return render(request, 'intempo/album_page.html', context=context_dict)

def add_review(request, album_id):
    if not request.is_ajax or request.method != 'POST':
        return not_found(request)
    
    if request.user.is_anonymous:
        return JsonResponse({'error': "You aren't authenticated! Please log in to add a review."}, status=400)
    
    user = UserProfile.objects.get(user=request.user)
    try:
        album = Album.objects.get(id=album_id)
    except Album.DoesNotExist:
        print("Album doesn't exist!")
        return JsonResponse({'error': 'Unexpected error! Please try again!'}, status=400)
    
    if user.has_rated(album):
        return JsonResponse({'error': "You have already rated this album!"}, status=400)

    form = AddReviewForm(request.POST)
    if form.is_valid():
        review = form.save(commit=False)
        review.album = album
        review.user = user
        review.save()
        messages.success(request, f"The review has been added!")

        return JsonResponse({
            'avg_rating': album.avg_rating, 
            'user_rating': review.rating, 
            'review_text': review.review_text,
            'profile_picture': str(user.profile_picture),
            'username': user.username,
            'review_id': review.id,
            'no_of_reviews': len(Review.for_album(album))
        }, status=200)
    else:
        print(form.errors)
        return JsonResponse({'error': "The form wasn't valid!"}, status=400)

def add_comment(request, review_id):
    if not request.is_ajax or request.method != 'POST':
        return not_found(request)
    
    if request.user.is_anonymous:
        return JsonResponse({'error': "You aren't authenticated! Please log in to add a comment."}, status=400)
    
    try:
        review = Review.objects.get(id=review_id)
    except Review.DoesNotExist:
        print("Review doesn't exist!")
        return JsonResponse({'error': 'Unexpected error! Please try again!'}, status=400)
        
    form = AddCommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.review = review
        user = UserProfile.objects.get(user=request.user)
        comment.user = user
        comment.save()
        messages.success(request, f"The comment has been added!")

        return JsonResponse({
            'comment_text': comment.comment_text,
            'profile_picture': str(user.profile_picture),
            'username': user.username,
            'no_of_comments': len(review.comments),
        }, status=200)
    else:
        print(form.errors)
        return JsonResponse({'error': "The form wasn't valid!"}, status=400)

def add_album(request):
    form = AddAlbumForm()
    if request.method == 'POST':
        form = AddAlbumForm(request.POST, request.FILES)

        if form.is_valid():

            Album = form.save(commit=False)
            Album.album_cover = request.FILES['album_cover']
            Album.save()
            messages.success(request, f"New album has been added")
            return redirect(reverse("intempo:albums"))
        else:
            print(form.errors)

    context_dict = {}
    context_dict["form"] = form

    response = render(request, 'intempo/add_album.html', context=context_dict)
    return response

def profile(request, username):
    try:
        profile = UserProfile.get_by_username(username)
    except UserProfile.DoesNotExist:
        return not_found(request)

    if request.method == 'POST':
        u_form = UpdateUserForm(request.POST, instance = request.user)
        p_form = UpdateUserProfileForm(request.POST, request.FILES, instance = UserProfile.objects.all().get(user=request.user))

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            return redirect(reverse("intempo:profile"))
    elif request.user == User.objects.get(username=username):
        u_form = UpdateUserForm(instance = request.user)
        p_form = UpdateUserProfileForm(instance=UserProfile.objects.all().get(user=request.user))
    else:
        u_form = None
        p_form = None

    context_dict = {}
    context_dict["username"] = username
    context_dict["user_id"] = profile.id
    context_dict["join_date"] = profile.time_since_joined
    context_dict["profile_picture"] = profile.profile_picture
    context_dict["u_form"] = u_form
    context_dict["p_form"] = p_form
    context_dict["Albums"] = profile.collection
    context_dict["Similar"] = profile.similar_profiles
    context_dict["this_user"] = request.user == User.objects.get(username=username)

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
        profile_form = UserProfileForm(request.POST, request.FILES)

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
            messages.success(request, f"your account has been created")
            return redirect(reverse("intempo:login"))
        else:
            print(user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(request, "intempo/signup.html", context = {"user_form": user_form, "profile_form": profile_form, "registered": registered})
