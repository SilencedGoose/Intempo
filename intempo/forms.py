from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator
from django.forms.widgets import NumberInput
from django.utils import timezone
from django.core.files.images import get_image_dimensions

from datetime import datetime

from intempo.models import UserProfile, Album, Review, Comment, get_all_tags

## USER REGISTRATION
class UserForm(forms.ModelForm):
    username = forms.CharField(max_length=30)
    password = forms.CharField(
        max_length=30, 
        widget=forms.PasswordInput()
    )
    
    class Meta:
        model = User
        fields = ('username', 'password',)

def CheckPicture(picture):
    if picture:
        width, height = get_image_dimensions(picture)
        if width != height:
            raise ValidationError(_("The image isn't a square!"))

class UserProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(
        label="Add Profile Picture (Optional)", 
        required = False,
    )

    class Meta:
        model = UserProfile
        fields = ('profile_picture',)

class AlbumForm(forms.Form):
    fltr = forms.CharField(
        label="Filter by Tags:",
        required = False, 
        help_text = "Separate the tags by a comma. Available Tags: " + ", ".join(get_all_tags())
    )
    search = forms.CharField(
        label="Search Album:", 
        required = False, 
        help_text = "Search by album name or title"
    )

    class Meta:
        fields = ('fltr', 'search')

#album form
class AddAlbumForm(forms.ModelForm):
    name = forms.CharField(
        label = "Name", 
        max_length = 30
    )
    artist = forms.CharField(
        label = "Artist", 
        max_length = 30
    )
    creation_date = forms.DateField(
        label="Creation Date",
        widget=forms.TextInput(
            attrs={'type': 'date'}
        ),
    )
    album_cover = forms.ImageField(
        label="Add Album Cover (Optional)", 
        required = False,
        validators=[CheckPicture],
        help_text = "The image must be a square."
    )
    description = forms.CharField(label="Add Description")
    tags = forms.Field(label="Add Tags")

    class Meta:
        model = Album
        fields = ('name', 'artist', 'creation_date', 'album_cover', 'description', 'tags')

def ValidateRating(rating):
    possible_ratings = [i/10 for i in range(0, 101)]
    if rating not in possible_ratings:
        raise ValidationError(
            _('%(value) must have at most 1 decimal place!'),
            params={'value': rating},
            )    

#review form
class AddReviewForm(forms.ModelForm):
    rating = forms.FloatField(
        label="Rating", 
        max_value=10, 
        min_value=0, 
        initial=5.0, 
        widget=NumberInput(attrs={'step': '0.1'}),
        validators=[MaxValueValidator(10), MinValueValidator(0), ValidateRating]
    )
    review_text = forms.CharField(
        label="Add a comment with your review (Optional)", 
        widget = forms.Textarea(attrs={'rows': 2}), 
        required=False
    )

    class Meta:
        model = Review
        fields = ('rating', 'review_text')

class AddCommentForm(forms.ModelForm):
    comment_text = forms.CharField(
        label = "Comment",
        widget = forms.Textarea(attrs={'rows': 2}), 
    )
    class Meta:
        model = Comment
        fields = ('comment_text',)

class UpdateUserProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(
        label="Update Profile Picture", 
    )

    class Meta:
        model = UserProfile
        fields = ('profile_picture',)
