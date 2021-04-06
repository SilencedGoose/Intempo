from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from datetime import datetime, timedelta
import os

BaseCommand.requires_system_checks = False

class Album(models.Model):
    name = models.CharField(max_length=30)
    artist = models.CharField(max_length=30)
    creation_date = models.DateField()
    album_cover = models.ImageField(upload_to="cover_art", default="Cover_Art/default_cover.png")
    description = models.TextField()
    tags = models.TextField()

    def __str__(self):
        return self.name

    @property
    def tags_as_list(self):
        """
        Returns the tags as a list
        """
        if len(self.tags) == 0:
            return []
        return [tag.strip() for tag in self.tags.lower().split(",")]

    @property
    def avg_rating(self):
        """
        Returns the average rating of the album to one decimal place
        """
        reviews = Review.objects.filter(album=self)
        if len(reviews) == 0:
            return 0.0
        ratings = [review.rating for review in reviews]
        return round(sum(ratings)/len(ratings), 1)

    @property
    def time_of_creation(self):
        """
        Returns the time of creation as a well-formatted string
        """
        return self.creation_date.strftime('%d %b %Y')

    @staticmethod
    def trending():
        """
        Returns at max 5 albums which have gotten the most reviews in the last 4 weeks
        """
        recent_review_count = {}
        time_now = timezone.now()
        # keep track of the number of reviews an album has received in the last 4 weeks
        for review in Review.objects.all():
            # review.time_posted is a date, but can only operate on a datetime
            posted_time = review.time_posted
            if posted_time > time_now - timedelta(weeks=4):
                count = recent_review_count.get(review.album, 0)
                recent_review_count[review.album] = count + 1

        # take the top 5 elements from the dictionary with the highest review count
        trending_albums = [key for key, value in sorted(recent_review_count.items(), reverse=True, key=lambda entry:entry[1])][:5]
        return trending_albums

    @staticmethod
    def top_rated():
        """
        Returns the top 5 albums with the highest average rating
        """
        return sorted(Album.objects.all(), key=lambda album:album.avg_rating, reverse=True)[:5]

    @staticmethod
    def filter_by_tags(tags):
        """
        Returns all the albums which have one of the tags provided. 
        The values aren't case sensitive.
        """
        tags = [tag.strip().lower() for tag in tags.split(',')]
        if tags == [""]:
            return Album.objects.all()
        
        albums = []
        ##checks if one search term is in the album info list
        for album in Album.objects.all():
            for tag in tags:
                if tag in album.tags_as_list and album not in albums:
                    ##adds to filtered album if so
                    albums.append(album)
        return albums

    def satisfies(self, keywords):
        """
        Returns true if the name or the artist of the album is a keyword.
        """
        keywords = keywords.split(" ")
        for keyword in keywords:
            if keyword.upper() in self.name.upper() or keyword.upper() in self.artist.upper():
                return True
        return False

def get_all_tags():
    """
    Returns all the tags in all the albums
    """
    tags = []
    albums = Album.objects.all()
    for album in albums:
        for tag in album.tags_as_list:
            if tag.lower() not in tags:
                tags.append(tag.lower())
    return tags

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user_profile")
    profile_picture = models.ImageField(upload_to="profile_pictures", default="profile_pictures/default_pic.png")
    join_date = models.DateTimeField(default=timezone.now)

    @staticmethod
    def get_by_username(username):
        """
        Returns a user profile given the username
        """
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise UserProfile.DoesNotExist("User matching query does not exist.")
        return UserProfile.objects.get(user=user)

    @property
    def username(self):
        return self.user.username

    def __str__(self):
        return self.user.username

    @property
    def similar_profiles(self):
        """
        Returns profiles similar to the user
        """
        # if the user hasn't rated at least 3 profiles, return an empty list
        reviews = Review.objects.filter(user=self)
        if (len(reviews) < 3):
            return []
        distance_dict = {}

        # Otherwise, for all the albums the user has rated:
        for self_review in reviews:
            # get all the reviews on this album
            all_ratings = Review.objects.filter(album=self_review.album)
            # for all the ratings given to the album (not from self)
            for other_review in all_ratings:
                if self_review != other_review:
                    # add to the distance value the distance between the ratings of the 2 reviews. Also, increment the count
                    value, count = distance_dict.get(other_review.user, (0, 0))
                    distance_dict[other_review.user] = (value + (other_review.rating - self_review.rating) ** 2, count + 1)

        # change from tuple of (value, count) to average by computing value/count.
        # Also, must have at least rated 2 albums in common.
        distance_dict = {key: value/count for key, (value, count) in distance_dict.items() if count >= 2}

        # take the top 3 elements from the dictionary with the smallest distance value
        similar_profiles = [key for key, value in sorted(distance_dict.items(), key=lambda entry:entry[1])][:3]
        return similar_profiles

    @property
    def collection(self):
        """
        Returns all the albums that the user has rated above 5
        """
        collection = []
        for review in Review.objects.filter(user=self):
            # assumes a user could have only given one rating to an album
            if review.rating >= 5:
                collection.append(review.album)
        return sorted(collection, key=lambda album:album.avg_rating)

    @property
    def time_since_joined(self):
        """
        Returns a well-formatted string representing the time passed since the user joined
        """
        return formatted_difference(self.join_date)

    def has_rated(self, album):
        """
        Returns true if the user has rated the album, false if the user hasn't rated the album
        """
        for review in Review.objects.all():
            if review.user == self and review.album == album:
                return True
        return False

class Review(models.Model):
    time_posted = models.DateTimeField(default=timezone.now)
    review_text = models.TextField(blank=True)
    rating = models.FloatField()
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    album = models.ForeignKey(Album, on_delete=models.CASCADE)

    def __str__(self):
        return self.review_text

    @property
    def time_since_posted(self):
        """
        Returns a well-formatted string representing the time passed since the review was posted
        """
        return formatted_difference(self.time_posted)

    @staticmethod
    def for_album(album):
        """
        Returns all the reviews (with non-empty review_text) for an album in chronological order
        """
        reviews = Review.objects.filter(album=album).order_by('-time_posted')
        return [review for review in reviews if len(review.review_text) > 0]

    @property
    def comments(self):
        """
        Returns all the comments for this review in chronological order
        """
        return Comment.objects.filter(review=self).order_by('-time_posted')

class Comment(models.Model):
    time_posted = models.DateTimeField(default=timezone.now)
    comment_text = models.TextField()
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    review = models.ForeignKey(Review, on_delete=models.CASCADE)

    def __str__(self):
        return self.comment_text

    @property
    def time_since_posted(self):
        """
        Returns a well-formatted string representing the time passed since the comment was posted
        """
        return formatted_difference(self.time_posted)

def formatted_difference(time):
    """
    Returns the difference between the time given and the time now in a well-formatted string (similar to YouTube string)
    """
    diff = timezone.now() - time
    sec_diff = round(diff.total_seconds()//1)
    # less than 60s ago -> Just now
    if sec_diff < 60:
        return "Just now"

    min_diff = sec_diff//60
    # 1 min -> 1 minute ago
    if min_diff == 1:
        return "1 minute ago"
    # 2-60 min -> .. minutes ago
    if min_diff < 60:
        return str(min_diff) + " minutes ago"

    hr_diff = min_diff//60
    if hr_diff == 1:
        return "1 hour ago"
    if hr_diff < 24:
        return str(hr_diff) + " hours ago"

    day_diff = hr_diff//24
    if day_diff == 1:
        return "1 day ago"
    if day_diff < 31:
        return str(day_diff) + " days ago"

    month_diff = day_diff//30
    if month_diff == 1:
        return "1 month ago"
    if month_diff < 12:
        return str(month_diff) + " months ago"

    year_diff = day_diff//365
    if year_diff == 1:
        return "1 year ago"
    return str(year_diff) + " years ago"
