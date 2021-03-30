from django import forms
from django.contrib.auth.models import User
from intempo.models import UserProfile, Album, Review, Comment
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator
from django.forms.widgets import NumberInput


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
    def get_tags():
        tags = []
        tag_str = ""
        album = Album.objects.all()
        for i in album:
            for j in i.tags_as_list:
                if j.lower() not in tags:
                    tags.append(j.lower())
                    tag_str = tag_str + j.lower() + " | "
                    
        tag_str = tag_str[0:len(tag_str)-2:]
        return tag_str
        
        
    filter = forms.CharField(required = False, help_text = get_tags() )
    DB_Fields = list((f.name,u""+(" ".join(f.name.split("_")))) for f in Album._meta.fields[1:4:])
    DB_Fields.append(("avg_rev","Average Review"))
    sort = forms.ChoiceField(choices=DB_Fields, required = False)
    search = forms.CharField(required = False)


    
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
