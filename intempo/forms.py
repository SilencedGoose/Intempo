from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator
from django.forms.widgets import NumberInput
from django.utils import timezone

from datetime import datetime

from intempo.models import UserProfile, Album, Review, Comment

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
        
def get_tags():
    tags = []
    album = Album.objects.all()
    for i in album:
        for j in i.tags_as_list:
            if j.lower() not in tags:
                tags.append(j.lower())
                
    return " | ".join(tags)

class AlbumForm(forms.Form):
    fltr = forms.CharField(label="Filter by Tags:", required = False, help_text = "Available Tags: " + get_tags())
    search = forms.CharField(label="Search Album:", required = False, help_text = "Search by album name or title")

    class Meta:
        fields = ('fltr', 'search')

#album form
class AddAlbumForm(forms.ModelForm):
    name = forms.CharField(label = "Name", max_length = 30)
    artist = forms.CharField(label = "Artist", max_length = 30)
    creation_date = forms.DateField(
        label="Creation Date",
        widget=forms.TextInput(
            attrs={'type': 'date'}
        ),
    )
    album_cover = forms.ImageField(label="Add Album Cover", max_length = 60, required = False)
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

class UpdateUserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('username', 'email')

class UpdateUserProfileForm(forms.ModelForm):
    
    class Meta:
        model = UserProfile
        fields = ('profile_picture',)
