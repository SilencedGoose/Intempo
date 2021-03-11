from django.db import models
from django.contrib.auth.models import User

class Album(models.Model):
    name = models.CharField(max_length=30)
    artist = models.CharField(max_length=30)
    creation_date = models.DateField()
    album_cover = models.ImageField(upload_to="album_covers", blank=True)
    description = models.TextField()
    tags = models.TextField()

    def __str__(self):
        return self.name

    @property
    def avg_review(self):
        """
        Returns the average rating of the album to one decimal place
        """
        reviews = Review.objects.filter(album=self)
        if len(reviews) == 0:
            return 0.0
        ratings = [review.rating for review in reviews]
        return round(sum(ratings)/len(ratings), 1)

# finds/creates the "deleted_user" (also implies that this isn't a valid username?)
def get_sentinel_user():
    return User.objects.get_or_create(username='deleted_user')[0]

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET(get_sentinel_user))
    profile_picture = models.ImageField(upload_to="profile_images", blank=True)
    join_date = models.DateField()

    @staticmethod
    def getByUsername(username):
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
        if (len(reviews) <= 3):
            return None
        distance_dict = {}

        # Otherwise, for all the albums the user has rated:
        for self_review in reviews:
            # get all the reviews on this album
            all_ratings = Review.objects.filter(album=self_review.album)
            # for all the ratings given to the album (not from self)
            for other_review in all_ratings:
                if self_review != other_review:
                    # add to the distance value the distance between the ratings of the 2 reviews
                    distance_dict[rating.user] = distance_dict.get(other_review.user, 0) + (other_review.rating - self_review.rating) ** 2

        # take the top 3 elements from the dictionary with the smallest distance value
        similar_profiles = [key for key, value in sorted(distance_dict.items(), key=lambda entry:entry[1])][:3]
        return similar_profiles

class Review(models.Model):
    time_posted = models.DateField()
    review_text = models.TextField()
    rating = models.FloatField()
    # when the user gets deleted, we add their reviews under the name "deleted_user"
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    album = models.ForeignKey(Album, on_delete=models.CASCADE)

    def __str__(self):
        return self.review_text

class Comment(models.Model):
    time_posted = models.DateField()
    comment_text = models.TextField()
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    review = models.ForeignKey(Review, on_delete=models.CASCADE)

    def __str__(self):
        return self.comment_text
