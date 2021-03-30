from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from intempo.models import Album, UserProfile, Review
from django.contrib.auth.models import User
from intempo.forms import UserForm, UserProfileForm, AddAlbumForm, AddReviewForm, AlbumForm, UpdateUserForm, UpdateUserProfileForm, AddCommentForm
from django.http import JsonResponse

def index(request):
    context_dict = {
        "trending": Album.trending(),
        "top": Album.top_rated()
    }

    response = render(request, 'intempo/index.html', context=context_dict)
    return response

def format_albums(albums, sort_type):
    """
    Given a list of albums and the sort type, sorts the albums by the sort type, 
    and then returns a JSON response unpacking the albums
    """
    if sort_type == 'name':
        albums = sorted(albums, key=lambda a:a.name)
    elif sort_type == 'artist':
        albums = sorted(albums, key=lambda a:a.artist)
    elif sort_type == 'avg_rating':
        albums = sorted(albums, key=lambda a:a.avg_rating, reverse=True)
    else:
        raise ValueError("Unexpected sort type!")

    return JsonResponse({
        'albums': [{
            'url': reverse("intempo:album_page", kwargs={'album_id': album.id}),
            'cover': '/media/' + str(album.album_cover),
            'name': album.name,
            'time_of_creation': album.time_of_creation,
            'artist': album.artist,
            'avg_rating': album.avg_rating,
        } for album in albums]
    }, status=200)

def add_album(request):
    if not request.is_ajax or request.method != 'POST':
        return not_found(request)
    
    if request.user.is_anonymous:
        return JsonResponse({'error': "You aren't authenticated! Please log in to add an album."}, status=400)
    
    form = AddAlbumForm(request.POST, request.FILES)
    if form.is_valid():
        album = form.save(commit=False)
        if 'album_cover' in request.FILES:
            album.album_cover = request.FILES['album_cover']
        album.save()
        albums = Album.objects.all()
        try:
            return format_albums(albums, 'avg_rating')
        except ValueError:
            print("Unexpected sort type!")
            return JsonResponse({'error': 'Unexpected error! Please try again!'}, status=400)
    else:
        return JsonResponse({'error': form.errors.as_json()}, status=400)

def sort_albums(request, sort_type):
    if not request.is_ajax or request.method != 'POST':
        return not_found(request)
    
    form = AlbumForm(request.POST)

    if form.is_valid():
        # filter by the tags
        albums = Album.filter_by_tags(form.cleaned_data["fltr"])

        # search albums 
        if form.cleaned_data["search"]:
            search = form.cleaned_data["search"]
            albums = [album for album in albums if album.by_filter(search)]

        try:
            return format_albums(albums, sort_type)
        except ValueError:
            print("Unexpected sort type!")
            return JsonResponse({'error': 'Unexpected error! Please try again!'}, status=400)
    else:
        return JsonResponse({'error': form.errors.as_json()}, status=400)

def albums(request):
    context_dict = {}
    
    context_dict["albums"] = sorted(Album.objects.all(), key=lambda a:a.avg_rating, reverse=True)
    context_dict["tags_form"] = AlbumForm()
    context_dict["add_album_form"] = AddAlbumForm()
    
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
        return JsonResponse({'error': form.errors.as_json()}, status=400)

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

        return JsonResponse({
            'comment_text': comment.comment_text,
            'profile_picture': str(user.profile_picture),
            'username': user.username,
            'no_of_comments': len(review.comments),
        }, status=200)
    else:
        return JsonResponse({'error': form.errors.as_json()}, status=400)

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

def not_found(request):
    response = render(request, '404.html', context={})
    return response

### USER AUTHENTICATION
def signup(request):
    registered = False
    context_dict = {}

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
            return redirect(reverse("intempo:login"))
        else:
            print(user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    context_dict["user_form"] = user_form
    context_dict["profile_form"] = profile_form
    context_dict["registered"] = registered
    return render(request, "intempo/signup.html", context=context_dict)
