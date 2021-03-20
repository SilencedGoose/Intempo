from django import forms
from django.contrib.auth.models import User
from intempo.models import UserProfile, Album, Review



## USER REGISTRATION
class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password',)


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('profile_picture',)

#album form
class AddAlbumForm(forms.ModelForm):
    
    name = forms.CharField(help_text = "name")
    artist = forms.CharField(help_text = "artist")
    creation_date = forms.DateField(help_text="creation date")
    album_cover = forms.ImageField(help_text="add album cover")
    description = forms.CharField(help_text="add description")
    tags = forms.Field(help_text="add tags")

    class Meta:
        model = Album
        fields = ('name', 'artist', 'creation_date', 'album_cover', 'description', 'tags')

#review form
class AddReviewForm(forms.ModelForm):
    review_text = forms.CharField(help_text="write review here")
    rating = forms.Field(help_text="add a rating")

    class Meta:
        model = Review
        fields = ('review_text', 'rating',)
