from django.test import TestCase

class ViewTestCase(TestCase):
# Login button in navbar not present if authenticated

# Login button in navbar present if not authenticated

# Logout button in navbar present if authenticated

# Logout button in navbar not present if not authenticated

# A wrong url loads the 404 page

    def test_sign_in_works_correctly(self):
        pass

    def test_sign_in_raises_error(self):
        pass

    def test_sign_up_works_correctly(self):
        pass

    def test_sign_up_raises_error(self):
        pass
    
    def test_add_album_works_correctly(self):
        pass

    def test_add_album_raises_error(self):
        pass

    def test_add_review_works_correctly(self):
        pass

    def test_add_review_raises_error(self):
        pass

    def test_add_comment_works_correctly(self):
        pass

    def test_add_comment_raises_error(self):
        pass

# Without any content in the db, the pages load fine
