import os

from django.db import models
from django.contrib.auth.models import User

from datetime import datetime, timedelta

class Album(models.Model):
    name = models.CharField(max_length=30, unique=True)
    artist = models.CharField(max_length=30)
    creation_date = models.DateField()
    album_cover = models.ImageField(upload_to="cover_art", default=os.path.join(os.path.dirname(__file__), "cover_art/default_cover.png"))
    description = models.TextField()
    tags = models.TextField()

    def __str__(self):
        return self.name

    def set_tags(self, tags):
        """
        Sets the list of tags into the album
        """
        self.tags = ", ".join(tags)
        self.save()

    @property
    def tags_as_list(self):
        """
        Returns the tags as a list
        """
        if len(self.tags) == 0:
            return []
        return self.tags.split(", ")

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
        time_now = datetime.now()
        # keep track of the number of reviews an album has received in the last 4 weeks
        for review in Review.objects.all():
            # review.time_posted is a date, but can only operate on a datetime
            posted_time = datetime.combine(review.time_posted, datetime.min.time())
            if posted_time < time_now - timedelta(weeks=4):
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
    def filter_by_tag(tag):
        """
        Returns all the albums which have the tag provided
        """
        return [album for album in Album.objects.all() if tag in album.tags_as_list]

# finds/creates the "deleted_user" (also implies that this isn't a valid username?)
def get_sentinel_user():
    return User.objects.get_or_create(username='deleted_user')[0]

class UserProfile(models.Model):
    # when the user gets deleted, we assign their reviews as get_sentinel_user
    user = models.OneToOneField(User, on_delete=models.SET(get_sentinel_user))
    profile_picture = models.ImageField(upload_to="profile_pictures", default=os.path.join(os.path.dirname(__file__), "profile_pictures/default_pic"))
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
    def collection(self):
        """
        Returns all the albums that the user has rated above 7
        """
        collection = []
        for review in Review.objects.filter(user=self):
            # assumes a user could have only given one rating to an album
            if review.rating >= 7:
                collection.append(review.album)
        return collection
    
    @property
    def time_since_joined(self):
        """
        Returns a well-formatted string representing the time passed since the user joined
        """
        return formatted_difference(date_to_datetime(self.join_date))
    
    def has_rated(self, album):
        """
        Returns true if the user has rated the album, false if the user hasn't rated the album
        """
        for review in Review.objects.all():
            if review.user == self and review.album == album:
                return True
        return False

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
        return formatted_difference(date_to_datetime(self.time_posted))

    @staticmethod
    def for_album(album):
        """
        Returns all the reviews for an album in chronological order
        """
        return Review.objects.filter(album=album).order_by('-time_posted')

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
        return formatted_difference(date_to_datetime(date_to_datetime(self.time_posted)))

def date_to_datetime(time):
    return datetime.combine(time, datetime.min.time())


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