from django import forms
from django.contrib.auth.models import User
from intempo.models import UserProfile, Album, Review, Comment
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
        
        
        
        
class AlbumForm(forms.ModelForm):
    filter = forms.CharField(help_text = "filter by tags",required = False)
    DB_Fields = list((f.name,u""+(" ".join(f.name.split("_")))) for f in Album._meta.fields[1:4:])
    DB_Fields.append(("avg_rev","Average Review"))
    sortby = forms.ChoiceField(choices=DB_Fields, help_text = "sort by")
    
    class Meta:
            model = Album
            fields = ()
    
    
        

#album form
class AddAlbumForm(forms.ModelForm):
    
    name = forms.CharField(label = "name", max_length = 30)
    artist = forms.CharField(label = "artist", max_length = 30)
    creation_date = forms.DateField(label="creation date")
    creation_date.clean
    album_cover = forms.ImageField(label="add album cover", max_length = 60)
    description = forms.CharField(label="add description", widget = forms.Textarea)
    tags = forms.Field(label="add tags")

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
    review_text = forms.CharField(label="write review here", widget = forms.Textarea)
    rating = forms.FloatField(label="add a rating", initial=0.0, validators=[validate_rating])

    class Meta:
        model = Review
        fields = ('review_text', 'rating',)

class AddCommentForm(forms.ModelForm):
    comment_text = forms.CharField(label = "add comment");
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
