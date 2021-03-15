import os

from django.db import models
from django.contrib.auth.models import User

from datetime import datetime

class Album(models.Model):
    name = models.CharField(max_length=30)
    artist = models.CharField(max_length=30)
    creation_date = models.DateField()
    album_cover = models.ImageField(upload_to="cover_art", blank=True)
    description = models.TextField()
    tags = models.TextField()

    def __str__(self):
        return self.name

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
    def time_since_creation(self):
        """
        Returns a well-formatted string representing the time passed since creation
        """
        return formatted_difference(self.creation_date)

# finds/creates the "deleted_user" (also implies that this isn't a valid username?)
def get_sentinel_user():
    return User.objects.get_or_create(username='deleted_user')[0]

class UserProfile(models.Model):
    # when the user gets deleted, we assign their reviews as get_sentinel_user
    user = models.OneToOneField(User, on_delete=models.SET(get_sentinel_user))
    profile_picture = models.ImageField(upload_to="profile_pictures", default=os.path.join(os.path.dirname(__file__), "profile_pictures/default_profile_pic"))
    join_date = models.DateField(default=datetime.now)

    @staticmethod
    def get_by_username(username):
        """
        Returns a user profile given the username
        """
        user = User.objects.get(username=username)
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
    def time_since_joined(self):
        """
        Returns a well-formatted string representing the time passed since the user joined
        """
        return formatted_difference(self.join_date)

class Review(models.Model):
    time_posted = models.DateField(default=datetime.now)
    review_text = models.TextField()
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

class Comment(models.Model):
    time_posted = models.DateField(default=datetime.now)
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
    diff = datetime.now() - time
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