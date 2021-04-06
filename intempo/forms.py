from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.files.images import get_image_dimensions
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms.widgets import NumberInput
from django.utils.translation import gettext_lazy as _

from .models import UserProfile, Album, Review, Comment, get_all_tags

def CheckPicture(picture):
    """
    Ensures the image is a square, if present.
    """
    if picture:
        width, height = get_image_dimensions(picture)
        if width != height:
            raise ValidationError(_("The image isn't a square!"))

# Sign up forms: UserForm for User model, and UserProfileForm for UserProfile model
class UserForm(forms.ModelForm):
    username = forms.CharField(max_length=30)
    password = forms.CharField(
        max_length=30, 
        widget=forms.PasswordInput()
    )
    
    class Meta:
        model = User
        fields = ('username', 'password',)

class UserProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(
        label="Add Profile Picture (Optional)", 
        required = False,
    )

    class Meta:
        model = UserProfile
        fields = ('profile_picture',)

# AlbumForm for searching/filtering albums
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

# AddAlbumForm to add a new album
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
    """
    Checks whether a rating between 0 and 10 is to 1 decimal place.
    """
    valid_ratings = [i/10 for i in range(0, 101)]
    if rating not in valid_ratings:
        raise ValidationError(
            _('%(value) must have at most 1 decimal place!'),
            params={'value': rating},
            )    

# AddReviewForm to add a new review
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

# AddCommentForm to add a new comment
class AddCommentForm(forms.ModelForm):
    comment_text = forms.CharField(
        label = "Comment",
        widget = forms.Textarea(attrs={'rows': 2}), 
    )
    class Meta:
        model = Comment
        fields = ('comment_text',)

# UpdateUserProfileForm to update profile picture
class UpdateUserProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(
        label="Update Profile Picture", 
    )

    class Meta:
        model = UserProfile
        fields = ('profile_picture',)
