from django.test import TestCase
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.template.response import TemplateResponse
from django.contrib.auth.models import User

from json import loads
from datetime import date

from .models import Album, Review, UserProfile, Comment

class SignUpFormTestCase(TestCase):
    def test_sign_up_raises_error(self):
        """
        Tests sign up raises an error if the password isn't provided
        """
        res = self.client.post(reverse("intempo:signup"), {'username': 'user'})

        # since the form wasn't valid, we should have gotten an error message
        self.assertEqual(type(res), HttpResponse, "The response wasn't an HttpResponse!")
        self.assertTrue("This field is required." in str(res.content), "Error message not found in the response!")
        
    def test_sign_up_works_correctly(self):
        """
        Tests whether sign up saves the userprofile/user
        """
        res = self.client.post(reverse("intempo:signup"), {'username': 'user', 'password': 'word'})

        # since the form was valid, we should have been redirected to login page
        self.assertEqual(type(res), HttpResponseRedirect, "The response isn't a redirect!")
        self.assertEqual(res.url, reverse("intempo:login"), "The response didn't redirect to the login page!")

        # filter by all the users with that username (not using "get" to avoid an error)
        users = User.objects.filter(username="user")
        self.assertEqual(len(users), 1, "The user wasn't saved!")

        userprofiles = UserProfile.objects.filter(user=users[0])
        self.assertEqual(len(userprofiles), 1, "The userprofile wasn't saved!")

        userprofile = userprofiles[0]

        # check time_since_joined is "Just now"
        self.assertEqual(userprofile.time_since_joined, "Just now", "The creation date value wasn't correctly added!")

        # check profile_picture is the default one
        self.assertEqual(userprofile.profile_picture, "profile_pictures/default_pic.png", "The profile picture wasn't the default one!")

def setup_user():
    """
    Sets up a user
    """
    user = User(username='user')
    user.set_password('123456')
    user.save()

    userprofile = UserProfile(user=user)
    userprofile.save()

class SignInFormTestCase(TestCase):
    def setUp(self):
        setup_user()
        
    def test_sign_in_raises_error(self):
        """
        Tests whether the sign in page raises an error if the password or username is wrong
        """
        res = self.client.post(reverse('intempo:login'), {'username': 'user0', 'password': '123456'})
        
        self.assertEqual(type(res), TemplateResponse, "The response isn't a template!")
        self.assertTrue("Please enter a correct username and password" in str(res.content))

    def test_sign_in_works_correctly(self):
        """
        Tests whether the sign in page redirects to homepage if the username/password are correct.
        """
        res = self.client.post(reverse('intempo:login'), {'username': 'user', 'password': '123456'})

        self.assertEqual(type(res),  HttpResponseRedirect, "The response isn't a redirect!")
        self.assertEqual(res.url, reverse('home'), "The redirected URL isn't the homepage!")

class AlbumFormTestCase(TestCase):
    def setUp(self):
        setup_user()

    def test_add_album_returns_404(self):
        """
        Tests whether going to the add_album page with a GET request returns a 404.
        """
        res = self.client.get(reverse("intempo:add_album"))

        self.assertEqual(type(res), HttpResponse, "The response isn't a HttpResponse!")
        self.assertTrue("The page you are looking for is unavailable" in str(res.content), "The returned page isn't the 404 page!")

    def test_add_album_does_not_work_if_anonymous_user(self):
        """
        Tests whether adding an album returns the correct JSONResponse if the user is anonymous.
        """
        res = self.client.post(reverse("intempo:add_album"), {})
        
        self.assertEqual(type(res), JsonResponse, "The response isn't a JsonResponse")
        self.assertEqual(res.status_code, 400, "Unexpected status code!")

        content = loads(res.content)
        self.assertTrue('error' in content, "The returned JSON doesn't have an error property")
        self.assertEqual(content['error'], "You aren't authenticated! Please log in to add an album.", "Unexpected error message receieved!")

    def test_add_album_does_not_work_with_single_issue_in_form(self):
        """
        Tests whether adding an album returns the correct JSONResponse if form has one issue.
        """
        self.client.login(username='user', password='123456')
        # missing creation_date
        res = self.client.post(reverse("intempo:add_album"), {
            'name': 'Album', 
            'artist': 'Artist', 
            'description': 'This is the description of the album',
            'tags': 'tag1'
        })
        
        self.assertEqual(type(res), JsonResponse, "The response isn't a JsonResponse")
        self.assertEqual(res.status_code, 400, "Unexpected status code!")

        content = loads(res.content)
        self.assertTrue('error' in content, "The returned JSON doesn't have an error property")
        error = loads(content["error"])

        self.assertTrue('creation_date' in error, "The returned JSON didn't recognise the error in creation_date field!")
        self.assertEqual(len(error["creation_date"]), 1, "The returned JSON doesn't have precisely one error for the creation_date field!")
        
        creation_date_error = error["creation_date"][0]
        self.assertEqual(creation_date_error["message"], "This field is required.", "Unexpected error message")
    
    def test_add_album_does_not_work_with_multiple_issues_in_form(self):
        """
        Tests whether adding an album returns the correct JSONResponse if form has multiple issues.
        """
        self.client.login(username='user', password='123456')
        # missing name and creation_date
        res = self.client.post(reverse("intempo:add_album"), {
            'artist': 'Artist', 
            'description': 'This is the description of the album',
            'tags': 'tag1'
        })
        
        self.assertEqual(type(res), JsonResponse, "The response isn't a JsonResponse")
        self.assertEqual(res.status_code, 400, "Unexpected status code!")

        content = loads(res.content)
        self.assertTrue('error' in content, "The returned JSON doesn't have an error property")
        error = loads(content["error"])
        
        # name error
        self.assertTrue('name' in error, "The returned JSON didn't recognise the error in name field!")
        self.assertEqual(len(error["name"]), 1, "The returned JSON doesn't have precisely one error for the name field!")
        name_error = error["name"][0]
        self.assertEqual(name_error["message"], "This field is required.", "Unexpected error message")

        # creation_date error
        self.assertTrue('creation_date' in error, "The returned JSON didn't recognise the error in creation_date field!")
        self.assertEqual(len(error["creation_date"]), 1, "The returned JSON doesn't have precisely one error for the creation_date field!")
        creation_date_error = error["creation_date"][0]
        self.assertEqual(creation_date_error["message"], "This field is required.", "Unexpected error message")

    def test_add_album_works_with_correct_data(self):
        """
        Tests whether adding an album returns the correct JSONResponse when provided with the right data.
        """
        self.client.login(username='user', password='123456')
        data = {
            'name': 'Album', 
            'artist': 'Artist', 
            'description': 'This is the description of the album',
            'tags': 'tag1',
            'creation_date': date(year=1986, month=5, day=3),
        }
        res = self.client.post(reverse("intempo:add_album"), data)
        
        self.assertEqual(type(res), JsonResponse, "The response isn't a JsonResponse")
        self.assertEqual(res.status_code, 200, "Unexpected status code!")
        
        # check the album was saved into the model
        albums = Album.objects.filter(name="Album")
        self.assertEqual(len(albums), 1, "The album wasn't saved!")
        album = albums[0]

        # check the JsonRespponse returned
        content = loads(res.content)
        self.assertTrue('albums' in content, "The returned JSON doesn't have albums!")
        self.assertEqual(len(content['albums']), 1, "Unexpected number of albums!")
        album_dict = content['albums'][0]

        del data['description']
        del data['tags']
        del data['creation_date']
        data['time_of_creation'] = "03 May 1986"
        data['cover'] = '/media/Cover_Art/default_cover.png'
        data['avg_rating'] = 0.0
        data['url'] = str(reverse('intempo:album_page', kwargs={'album_id': album.id}))
        self.assertEqual(album_dict, data, 'The returned JSON has incorrect values!')

def setup_album():
    album = Album(
        id=1,
        name="Album", 
        artist='Artist', 
        tags='tag1', 
        creation_date=date(year=1986, month=5, day=3), 
        description='This is the description of the album'
    )
    album.save()

class ReviewFormTestCase(TestCase):
    def setUp(self):
        setup_user()
        setup_album()

    def test_add_review_returns_404(self):
        """
        Tests whether calling the review view with a GET request returns a 404.
        """
        res = self.client.get(reverse("intempo:add_review", kwargs={'album_id': 1}))

        self.assertEqual(type(res), HttpResponse, "The response isn't a HttpResponse!")
        self.assertTrue("The page you are looking for is unavailable" in str(res.content), "The returned page isn't the 404 page!")

    def test_add_review_does_not_work_if_anonymous_user(self):
        """
        Tests whether adding a review returns the correct JSONResponse if the user is anonymous.
        """
        res = self.client.post(reverse("intempo:add_review", kwargs={'album_id': 1}), {})
        
        self.assertEqual(type(res), JsonResponse, "The response isn't a JsonResponse")
        self.assertEqual(res.status_code, 400, "Unexpected status code!")

        content = loads(res.content)
        self.assertTrue('error' in content, "The returned JSON doesn't have an error property")
        self.assertEqual(content['error'], "You aren't authenticated! Please log in to add a review.", "Unexpected error message receieved!")

    def test_add_review_does_not_work_with_issue_in_form(self):
        """
        Tests whether adding a review returns the correct JSONResponse if form has an issue.
        """
        self.client.login(username='user', password='123456')
        # missing rating
        res = self.client.post(reverse("intempo:add_review", kwargs={'album_id': 1}), {
            'review_text': "This is my review to this album"
        })
        
        self.assertEqual(type(res), JsonResponse, "The response isn't a JsonResponse")
        self.assertEqual(res.status_code, 400, "Unexpected status code!")

        content = loads(res.content)
        self.assertTrue('error' in content, "The returned JSON doesn't have an error property")
        error = loads(content["error"])

        self.assertTrue('rating' in error, "The returned JSON didn't recognise the error in rating field!")
        self.assertEqual(len(error["rating"]), 1, "The returned JSON doesn't have precisely one error for the rating field!")
        
        rating_error = error["rating"][0]
        self.assertEqual(rating_error["message"], "This field is required.", "Unexpected error message")
    
    def test_add_review_works_with_correct_data(self):
        """
        Tests whether adding a review returns the correct JSONResponse when provided with the right data.
        """
        self.client.login(username='user', password='123456')
        data = {
            'rating': 8.0,
            'review_text': "This is my review to this album"
        }
        res = self.client.post(reverse("intempo:add_review", kwargs={'album_id': 1}), data)

        self.assertEqual(type(res), JsonResponse, "The response isn't a JsonResponse")
        self.assertEqual(res.status_code, 200, "Unexpected status code!")
        
        # check the review was saved into the model
        reviews = Review.objects.filter(review_text="This is my review to this album")
        self.assertEqual(len(reviews), 1, "The review wasn't saved!")
        review = reviews[0]

        # check the JsonRespponse returned
        content = loads(res.content)
        data['user_rating'] = data['rating']
        del data['rating']
        data['avg_rating'] = 8.0
        data['profile_picture'] = 'profile_pictures/default_pic.png'
        data['username'] = 'user'
        data['review_id'] = 1
        data['no_of_reviews'] = 1
        self.assertEqual(content, data, 'The returned JSON has incorrect values!')

def setup_review():
    review = Review(
        id=1,
        review_text="This is my review to this album",
        rating=8.0,
        user=UserProfile.get_by_username("user"),
        album=Album.objects.get(id=1)
    )
    review.save()

class CommentFormTestCase(TestCase):
    def setUp(self):
        setup_user()
        setup_album()
        setup_review()

    def test_add_comment_returns_404(self):
        """
        Tests whether calling the comment view with a GET request returns a 404.
        """
        res = self.client.get(reverse("intempo:add_comment", kwargs={'review_id': 1}))

        self.assertEqual(type(res), HttpResponse, "The response isn't a HttpResponse!")
        self.assertTrue("The page you are looking for is unavailable" in str(res.content), "The returned page isn't the 404 page!")

    def test_add_comment_does_not_work_if_anonymous_user(self):
        """
        Tests whether adding a comment returns the correct JSONResponse if the user is anonymous.
        """
        res = self.client.post(reverse("intempo:add_comment", kwargs={'review_id': 1}), {})
        
        self.assertEqual(type(res), JsonResponse, "The response isn't a JsonResponse")
        self.assertEqual(res.status_code, 400, "Unexpected status code!")

        content = loads(res.content)
        self.assertTrue('error' in content, "The returned JSON doesn't have an error property")
        self.assertEqual(content['error'], "You aren't authenticated! Please log in to add a comment.", "Unexpected error message receieved!")

    def test_add_comment_does_not_work_with_single_issue_in_form(self):
        """
        Tests whether adding a comment returns the correct JSONResponse if form has one issue.
        """
        self.client.login(username='user', password='123456')
        res = self.client.post(reverse("intempo:add_comment", kwargs={'review_id': 1}), {})
        
        self.assertEqual(type(res), JsonResponse, "The response isn't a JsonResponse")
        self.assertEqual(res.status_code, 400, "Unexpected status code!")

        content = loads(res.content)
        self.assertTrue('error' in content, "The returned JSON doesn't have an error property")
        error = loads(str(content["error"]))

        self.assertTrue('comment_text' in error, "The returned JSON didn't recognise the error in comment_text field!")
        self.assertEqual(len(error["comment_text"]), 1, "The returned JSON doesn't have precisely one error for the comment_text field!")
        
        comment_text_error = error["comment_text"][0]
        self.assertEqual(comment_text_error["message"], "This field is required.", "Unexpected error message")
    
    def test_add_comment_works_with_correct_data(self):
        """
        Tests whether adding a comment returns the correct JSONResponse when provided with the right data.
        """
        self.client.login(username='user', password='123456')
        data = {'comment_text': 'This is the comment on this review'}
        res = self.client.post(reverse("intempo:add_comment", kwargs={'review_id': 1}), data)
        self.assertEqual(type(res), JsonResponse, "The response isn't a JsonResponse")
        self.assertEqual(res.status_code, 200, "Unexpected status code!")
        
        # check the album was saved into the model
        comments = Comment.objects.filter(comment_text="This is the comment on this review")
        self.assertEqual(len(comments), 1, "The comment wasn't saved!")
        comment = comments[0]

        # check the JsonRespponse returned
        content = loads(res.content)
        data['profile_picture'] = 'profile_pictures/default_pic.png'
        data['no_of_comments'] = 1
        data['username'] = 'user'
        self.assertEqual(content, data, 'The returned JSON has incorrect values!')

names = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"]

def setup_albums():
    for i in range(10):
        tags = ['tag' + str(j) for j in range(i)]
        album = Album(name=names[i], description="", artist=names[9-i], tags=",".join(tags), creation_date=date(2018, 4, 12))
        album.save()

def setup_reviews():
    profile = UserProfile.objects.get()
    for i in range(10):
        album = Album.objects.get(name=names[i])
        review = Review(user=profile, album=album, rating=i+1)
        review.save()

class SortingAndSearchingAlbumsTestCase(TestCase):
    def setUp(self):
        setup_user()
        setup_albums()
        setup_reviews()

    def test_album_sort_works(self):
        """
        Test sort_albums view works given a sort type
        """
        res = self.client.post(reverse('intempo:sort_albums', kwargs={'sort_type': 'name'}), {})
        self.assertEqual(type(res), JsonResponse, "The response isn't a JsonResponse")
        self.assertEqual(res.status_code, 200, "Unexpected status code!")
        
        content = loads(res.content)
        recv_albums = [album["name"] for album in content["albums"]]
        self.assertEqual(recv_albums, names, "The albums haven't been sorted correctly!")
    
    def test_album_search_works(self):
        """
        Test sort_albums view works given a search value
        """
        # albums a, c will be returned by their name; albums j, h will be returned by their artist
        res = self.client.post(reverse('intempo:sort_albums', kwargs={'sort_type': 'avg_rating'}), {'search': 'a c'})
        self.assertEqual(type(res), JsonResponse, "The response isn't a JsonResponse")
        self.assertEqual(res.status_code, 200, "Unexpected status code!")

        content = loads(res.content)
        recv_albums = [album["name"] for album in content["albums"]]

        # expect j, h, c, a (in that order since higher letters have higher ratings)
        self.assertEqual(recv_albums, ['j', 'h', 'c', 'a'],  "The albums weren't searched/sorted correctly!")

    def test_album_filter_works(self):
        """
        Test sort_album view works given a filter for tags
        """
        for i in range(9):
            res = self.client.post(reverse('intempo:sort_albums', kwargs={'sort_type': 'name'}), {'fltr': 'tag' + str(i)})
            self.assertEqual(type(res), JsonResponse, "The response isn't a JsonResponse")
            self.assertEqual(res.status_code, 200, "Unexpected status code!")

            content = loads(res.content)
            recv_albums = [album["name"] for album in content["albums"]]
            
            # expect albums from i+1 to 10 since those have the tag
            expected_albums = [names[j] for j in range(i+1, 10)]

            self.assertEqual(recv_albums, expected_albums,  "The albums weren't filtered/sorted correctly!")
