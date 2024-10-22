#!/usr/bin/env python
## run using python manage.py migrate --run-syncdb
## instead of python manage.py migrate

##Album images and information taking from RollingStone, and Google.

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'intempo_project.settings')

from json import load

import django
django.setup()

from datetime import datetime
django.setup()
from intempo.models import Album, UserProfile, Review, Comment

from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from django.utils.timezone import make_aware


def convert_to_date(list):
    """
    Converts a list of [day, month, year] into a datetime object
    """
    return datetime(day=list[0], month=list[1], year=list[2])


def populate():
    print("- Clearing pre-existing data")
    Album.objects.all().delete()
    UserProfile.objects.all().delete()
    Review.objects.all().delete()
    Comment.objects.all().delete()

    with open("population_data.json", encoding="utf-8") as f:
        data = load(f)

    print("- Adding albums")
    for myAlbum in data["albums"]:
        add_album(myAlbum)

    print("- Adding users")
    for myUser in data["users"]:
        add_user(myUser)

    print("- Adding reviews")
    for myReview in data["reviews"]:
        add_review(myReview)

    print("- Adding comments!")
    for myComment in data["comments"]:
        add_comment(myComment)

    print("Finished without any errors!")

def add_album(myAlbum):
    A = Album(
        name=myAlbum['name'],
        artist=myAlbum['artist'],
        creation_date = convert_to_date(myAlbum['creation_date']),
        album_cover = myAlbum['album_cover'],
        description = myAlbum['description'],
        tags = ",".join(myAlbum['tags'])
    )
    A.save()
    return A

def add_user(myUser):
    try:
        M = User.objects.create_user(myUser['username'], None, 'password')
    except IntegrityError:
        M = User.objects.get(username=myUser['username'])
    # M = User.objects.get_or_create(username=myUser['username'])[0]
    # M.set_password(myUser['password'])
    # M.save()
    U = UserProfile(
        join_date=make_aware(convert_to_date(myUser['join_date'])),
        user=M,
        profile_picture=myUser['profile_picture'],
    )

    U.save()
    return U

def add_review(myReview):
    R = Review(
        user=UserProfile.get_by_username(username=myReview['username']),
        album=Album.objects.get(name=myReview['album']),
        rating=myReview['rating'],
        time_posted=make_aware(convert_to_date(myReview['time_posted'])),
        review_text=myReview['review_text']
    )
    R.save()
    return R

def add_comment(myComment):
    C = Comment(
        time_posted=make_aware(convert_to_date(myComment['time_posted'])),
        user=UserProfile.get_by_username(username=myComment['username']),
        review=Review.objects.get(
            user=UserProfile.get_by_username(username=myComment['review'][0]),
            album=Album.objects.get(name=myComment['review'][1])
        ),
        comment_text=myComment['comment_text']
    )
    C.save()
    return C

if __name__ == '__main__':
    print('Starting Intempo population script...')
    populate()
