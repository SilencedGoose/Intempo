from datetime import datetime, timedelta

from django.utils import timezone
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils.timezone import make_aware

from .models import Album, Review, UserProfile, formatted_difference

# Album creation times
album_creation_time = [
    datetime(2010, 1, 2),
    datetime(2011, 2, 4),
    datetime(2012, 3, 6),
    datetime(2013, 4, 8),
    datetime(2014, 5, 10),
    datetime(2015, 6, 12),
    datetime(2016, 7, 14),
    datetime(2017, 8, 16),
    datetime(2018, 9, 18),
    datetime(2019, 10, 20),
]

def setup_albums():
    """
    Sets up the albums at the start
    """
    for i in range(10):
        tags = ["tag" + str(j) for j in range(i)]
        album = Album.objects.create(
            name="album" + str(i),
            artist="artist" + str(i),
            creation_date=make_aware(album_creation_time[i]),
            description="Album " + str(i),
            tags=",".join(["tag" + str(j) for j in range(i)])
        )

def setup_users():
    """
    Sets up the users at the start
    """
    for i in range(10):
        user = User.objects.create(username="user" + str(i))
        UserProfile.objects.create(user=user, join_date=timezone.now())

# The ratings for the 10 albums; the rating is provided by the n-th user
ratings = [
    # e.g. no user has rated album0
    [],
    # e.g. user0 rated album1 with 5.6
    [5.6],
    [4.4, 6.8],
    [5.9, 5.2, 5.6],
    # user2 and user3 have very different ratings for all the albums (their profiles aren't considered similar)
    [4.3, 7.8, 3.2, 8.0],
    # user3 and user4 have very similar ratings for all the albums (their profiles are considered similar)
    [8.6, 7.2, 9.4, 4.0, 4.3],
    [6.3, 9.6, 5.0, 9.4, 9.7, 4.8],
    [9.7, 7.3, 8.5, 3.5, 3.2, 7.2, 8.8],
    [8.2, 4.8, 9.9, 3.6, 3.6, 5.6, 6.9, 4.8],
    [5.9, 9.2, 3.9, 9.2, 9.5, 6.2, 6.8, 6.0, 6.9],
]

def setup_reviews():
    time_now = timezone.now()
    for i in range(10):
        album = Album.objects.get(name="album" + str(i))
        for j in range(i):
            user = UserProfile.get_by_username("user" + str(j))
            Review.objects.create(
                time_posted=time_now - timedelta(days=4*i), 
                review_text="This is the review text for album " + str(i) + " from user " + str(j), 
                rating=ratings[i][j], 
                album=album,
                user=user
            )

class AlbumTestCase(TestCase):
    def setUp(self):
        setup_albums()
        setup_users()
        setup_reviews()
    
    def test_time_of_creation(self):
        """
        Tests the property time_of_creation
        """
        first_10_months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct"]
        for i in range(10):
            album = Album.objects.get(name="album" + str(i))
            date = str(2*i+2)
            self.assertEqual(
                album.time_of_creation, ("0" + date if len(date) == 1 else date) + " " + first_10_months[i] + " 201" + str(i),
                "The time of creation of the album isn't formatted correctly!"
            )

    def test_avg_rating_with_ratings(self):
        """
        Tests the average rating for an album that already has ratings
        """
        # we check with albums1, .., albums9
        for i in range(1, 10):
            album = Album.objects.get(name="album" + str(i))
            self.assertEqual(album.avg_rating, round(sum(ratings[i])/i, 1), "The average rating of the album isn't correct!")
    
    def test_avg_rating_without_ratings(self):
        """
        Tests the average rating for an album that doesn't have ratings
        """
        # album0 has no reviews, so its avg_rating is 0.0
        album0 = Album.objects.get(name="album0")
        self.assertEqual(album0.avg_rating, 0.0, "The average rating functionality doesn't work if there are no albums reviewed!")
    
    def test_trending_albums(self):
        """
        Tests the static method trending albums 
        """
        trending_albums = Album.trending()
        # ranked by the count, so expect albums with higher index before those with lower index
        # but album9, album8, album7 don't appear because all of their reviews was before the last 4 weeks (4*7 >= 28, and so on)
        self.assertEqual(
            ["album6", "album5", "album4", "album3", "album2"],
            [album.name for album in trending_albums],
            "Trending albums doesn't return the last 5 albums"
        )


    def test_top_rated_albums(self):
        """
        Tests the static method top_rated albums
        """
        top_rated = Album.top_rated()
        avg_ratings = [(i, 0) if len(rating) == 0 else (i, sum(rating)/len(rating)) for i, rating in enumerate(ratings)]
        avg_ratings = sorted(avg_ratings, key=lambda rating:rating[1], reverse=True)
        for i in range(0, 10):
            album = Album.objects.get(name="album" + str(avg_ratings[i][0]))
            if i < 5:
                self.assertTrue(album in top_rated, "Expected album album" + str(avg_ratings[i][1]) + " in the top rated albums list!")
            else:
                self.assertFalse(album in top_rated, "Unexpected album album" + str(avg_ratings[i][1]) + " in the top rated albums list!")

    def test_tags_attribute(self):
        """
        Tests the tag attribute has correct values
        """
        for i in range(10):
            album = Album.objects.get(name="album"+str(i))
            tags = ["tag"+str(j) for j in range(i)]
            self.assertEqual(album.tags, "" if len(tags) == 0 else ",".join(tags), "The tags aren't correctly stored!")
    
    def test_filter_by_tags(self):
        """
        Tests the static method filter_by_tags
        """
        for i in range(10):
            tags = ["tag"+str(j) for j in range(i, 10)]
            albums = Album.filter_by_tags(",".join(tags))
            # only albums[i+1] to album9 have one of the tags {tag[i], tag[i+1], .., tag9}
            expected = [Album.objects.get(name="album"+str(j)) for j in range(i+1, 10)]
            self.assertEqual(albums, expected, "The static method filter_by_tags isn't working!")

class UserProfileTestCase(TestCase):
    def setUp(self):
        setup_albums()
        setup_users()
        setup_reviews()
    
    def test_get_by_username(self):
        """
        Tests the static property get_by_username
        """
        for i in range(10):
            user = User.objects.get(username="user" + str(i))
            userprofile = UserProfile.get_by_username("user" + str(i))
            self.assertEqual(userprofile.user, user, "The static method get_by_username didn't return the user!")
    
    def test_no_similar_profiles(self):
        """
        Tests whether the users who have reviewed less than (or equal to) 3 reviews have no similar profile
        """
        for i in range(7, 10):
            userProfile = UserProfile.get_by_username("user" + str(i))
            similar_profiles = userProfile.similar_profiles
            self.assertEqual(len(similar_profiles), 0, "Expected no profiles within similar_profiles")
    
    def test_has_similar_profiles(self):
        """
        Tests whether similar_profiles algorithm includes profiles when the user has more than 3 reviews.
        """
        for i in range(0, 7):
            userprofile = UserProfile.get_by_username("user" + str(i))
            similar_profiles = userprofile.similar_profiles
            # check there are at most 3 similar profiles
            self.assertTrue(len(similar_profiles) <= 3, "Expected at most 3 profiles from User.similar_profiles property!")

            # check the userprofile isn't one of the similar profiles
            self.assertTrue(userprofile not in similar_profiles, "Expected not to find the user within similar_profiles!")
    
    def test_similar_profiles_correctness(self):
        """
        Tests the correctness of the similar_profiles algorithm
        """
        user2 = UserProfile.get_by_username("user2")
        user3 = UserProfile.get_by_username("user3")
        user4 = UserProfile.get_by_username("user4")
        similar_profiles_user2 = user2.similar_profiles
        similar_profiles_user3 = user3.similar_profiles
        similar_profiles_user4 = user4.similar_profiles
        # 2 users who have very given very similar ratings to the same albums get recommended, i.e. user3 and user4
        # in fact, because they are the most similar they can be, i.e. it's in the first index
        self.assertTrue(user3 == similar_profiles_user4[0], "Expected user user3 in user4's similar_profiles")
        self.assertTrue(user4 == similar_profiles_user3[0], "Expected user user4 in user1's similar_profiles")

        # on the other hand, 2 users who have given very different ratings to the same albums do not get recommended, i.e. user2 and user3
        self.assertTrue(user2 not in similar_profiles_user3, "Unexpected user user2 in user3's similar_profiles")
        self.assertTrue(user3 not in similar_profiles_user2, "Unexpected user user3 in user2's similar_profiles")
    
    def test_user_has_rated(self):
        """
        Tests the function user.has_rated(album)
        """
        for i in range(10):
            user = UserProfile.get_by_username("user"+str(i))
            for j in range(10):
                album = Album.objects.get(name="album"+str(j))
                if i < j:
                    self.assertTrue(user.has_rated(album), "The user has rated the album, but the function returned not rated!")
                else:
                    self.assertFalse(user.has_rated(album), "The user hasn't rated the album, but the function returned rated!")
    
    def test_user_collection(self):
        """
        Tests the collection attribute of a user
        """
        for i in range(10):
            user = UserProfile.get_by_username("user"+str(i))
            collection = user.collection
            for j in range(10):
                album = Album.objects.get(name="album" + str(j))
                # if the user rated the profile by a value higher than 5, check it is in the collection
                if user.has_rated(album) and Review.objects.get(user=user, album=album).rating >= 5:
                    self.assertTrue(album in collection, "The album {a} should be in the collection of the user {u}!".format(a=album.name, u=user.username))
                else:
                # otherwise, check it's not in the collection
                    self.assertFalse(album in collection, "The album {a} shouldn't be in the collection of the user {u}!".format(a=album.name, u=user.username))

class ReviewTestCase(TestCase):
    def setUp(self):
        setup_albums()
        setup_users()
        setup_reviews()
    
    def test_for_album(self):
        """
        Tests the static method Review.for_album(album) returns albums the user has rated, and in chronological order
        """
        for i, album in enumerate(Album.objects.all()):
            # changes from queryset to normal list
            reviews = [review for review in Review.for_album(album)]
            self.assertEqual(len(reviews), i, "Expected {i} reviews for album{i}".format(i=i))
            sorted_reviews = sorted(reviews, key=lambda review:review.time_posted, reverse=True)
            self.assertEqual(reviews, sorted_reviews, "The reviews should have already been in chronological order!")

class DateTestCase(TestCase):
    def test_formatted_difference_less_than_a_minute(self):
        """
        Tests the function `formatted_difference` returns "Just now" if the difference in the time is less than a minute
        """
        for i in range(0, 60):
            self.assertEqual(formatted_difference(timezone.now() - timedelta(seconds=i)), "Just now", "Time difference being 0 doesn't return just now!")
    
    def test_formatted_difference_between_a_minute_and_an_hour(self):
        """
        Tests the function `formatted_difference` returns "i minute(s) ago" if the difference in time is i minute(s)
        """
        self.assertEqual(formatted_difference(timezone.now() - timedelta(minutes=1)), "1 minute ago", "Time difference of a minute doesn't return 1 minute ago!")
        for i in range(2, 60):
            self.assertEqual(formatted_difference(timezone.now() - timedelta(minutes=i)), str(i) + " minutes ago", "Time difference of {i} minutes doesn't return {i} minutes ago!".format(i=i))
    
    def test_formatted_difference_between_an_hour_and_a_day(self):
        """
        Tests the function `formatted_difference` returns "i hour(s) ago" if the difference in time is i hour(s)
        """
        self.assertEqual(formatted_difference(timezone.now() - timedelta(hours=1)), "1 hour ago", "Time difference of a hour doesn't return 1 hour ago!")
        for i in range(2, 24):
            self.assertEqual(formatted_difference(timezone.now() - timedelta(hours=i)), str(i) + " hours ago", "Time difference of {i} hours doesn't return {i} hours ago".format(i=i))
    
    def test_formatted_difference_between_a_day_and_a_month(self):
        """
        Tests the function `formatted_difference` returns "i day(s) ago" if the difference in time is i day(s)
        """
        self.assertEqual(formatted_difference(timezone.now()  - timedelta(days=1)), "1 day ago", "Time difference of a day doesn't return 1 day ago!")
        for i in range(2, 31):
            self.assertEqual(formatted_difference(timezone.now() - timedelta(days=i)), str(i) + " days ago", "Time difference of {i} days doesn't return {i} days ago!".format(i=i))
    
    def test_formatted_difference_between_a_month_and_a_year(self):
        """
        Tests the function `formatted_difference` returns "i month(s) ago" if the difference in time is i month(s)
        """
        self.assertEqual(formatted_difference(timezone.now() - timedelta(days=31)), "1 month ago", "Time difference of a month doesn't return 1 month ago!")
        for i in range(2, 12):
            self.assertEqual(formatted_difference(timezone.now() - timedelta(days=30*i+1)), str(i) + " months ago", "Time difference of {i} monthes doesn't return {i} months ago".format(i=i))
    
    def test_formatted_difference_above_a_year(self):
        """
        Tests the function `formatted_difference` returns "i year(s) ago" if the difference in time is i year(s)
        """
        self.assertEqual(formatted_difference(timezone.now() - timedelta(days=365)), "1 year ago", "Time difference of a year doesn't return 1 year ago!")
        for i in range(2, 10):
            self.assertEqual(formatted_difference(timezone.now() - timedelta(days=365*i+1)), str(i) + " years ago", "Time difference of {i} years ago doesn't return {i} years ago!".format(i=i))
