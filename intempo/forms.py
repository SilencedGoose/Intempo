from django import forms
from django.contrib.auth.models import User
from intempo.models import UserProfile, Album, Review
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _



## USER REGISTRATION
class UserForm(forms.ModelForm):
    password = forms.CharField(max_length=30, widget=forms.PasswordInput())
    username = forms.CharField(max_length=30)
    class Meta:
        model = User
        fields = ('username', 'email', 'password',)


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('profile_picture',)

#album form
class AddAlbumForm(forms.ModelForm):
    
    name = forms.CharField(help_text = "name", max_length = 30)
    artist = forms.CharField(help_text = "artist", max_length = 30)
    creation_date = forms.DateField(help_text="creation date")
    creation_date.clean
    album_cover = forms.ImageField(help_text="add album cover", max_length = 60)
    description = forms.CharField(help_text="add description", widget = forms.Textarea)
    tags = forms.Field(help_text="add tags")

    class Meta:
        model = Album
        fields = ('name', 'artist', 'creation_date', 'album_cover', 'description', 'tags')

#review form
class AddReviewForm(forms.ModelForm):
    def validate_rating(x):
        if (x > 10.0) or (x < 0.0):
            raise ValidationError(
            _('%(value) must be between 0 and 10 inclusive'),
            params={'value': value},
            )
    review_text = forms.CharField(help_text="write review here", widget = forms.Textarea)
    rating = forms.FloatField(help_text="add a rating", initial=0.0, validators=[validate_rating])



    class Meta:
        model = Review
        fields = ('review_text', 'rating',)

class UpdateUserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('username', 'email')

class UpdateUserProfileForm(forms.ModelForm):
    
    class Meta:
        model = UserProfile
        fields = ('profile_picture',)
