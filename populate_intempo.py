#!/usr/bin/env python
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'intempo_project.settings')

from json import load

import django
django.setup()

from datetime import datetime
django.setup()

from django.contrib.auth.models import User

from intempo.models import Album, UserProfile, Review, Comment

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
        description = myAlbum['description']
    )
    A.save()
    A.set_tags(myAlbum['tags'])
    return A
    
def add_user(myUser):
    M = User.objects.get_or_create(username=myUser['username'])[0]
    M.set_password(myUser['password'])
    M.save()
    U = UserProfile(
        join_date=convert_to_date(myUser['join_date']), 
        user=M,
        profile_picture=os.path.join(os.path.join(os.path.dirname(__file__), myUser['profile_picture'])),
    )
    U.save()
    return U
    
def add_review(myReview):
    R = Review(
        user=UserProfile.get_by_username(username=myReview['username']),
        album=Album.objects.get(name=myReview['album']),
        rating=myReview['rating'],
        time_posted=convert_to_date(myReview['time_posted']),
        review_text=myReview['review_text']
    )
    R.save()
    return R
    
def add_comment(myComment):
    C = Comment(
        time_posted=convert_to_date(myComment['time_posted']),
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
    