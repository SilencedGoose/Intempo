from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

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
    # Calculates the average reviews of the album to one decimal place
    def avg_review(self):
        reviews = Review.objects.filter(id=self.id)
        if len(reviews) == 0:
            return 0.0
        ratings = [review.rating for review in reviews]
        return round(sum(ratings)/len(ratings), 1)

# finds/creates the "deleted_user" (also implies that this isn't a valid username?)
def get_sentinel_user():
    return get_user_model().objects.get_or_create(username='deleted_user')[0]

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to="profile_images", blank=True)
    join_date = models.DateField()

    def __str__(self):
        return self.user.username

    # TODO: Complete
    # Returns profiles similar to the user
    def similar_profiles(self):
        # if the user hasn't rated at least 5 profiles, return an empty list
        similarityValue = {}

        # otherwise, for all the albums that this user has rated, add to similarityValue[user] (self.rating.value - user.rating.value)^2
        for user in UserProfile.objects.all():
            if user != self:
                # for all the albums the user (self) has rated,
                    # add to the squared distance between the the rating of the user and this user and save it in a map
                    pass

        # take the top 5 elements from the dictionary with the highest similarity value
        similar_profiles = [key for key, value in sorted(similarityValue.items(), key=lambda entry:entry[1], reverse=True)][:5]
        return similar_profiles

class Review(models.Model):
    time_posted = models.DateField()
    review_text = models.TextField()
    rating = models.FloatField()
    # when the user gets deleted, we add their reviews under the name "deleted_user"
    user = models.ForeignKey(UserProfile, on_delete=models.SET(get_sentinel_user))
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
