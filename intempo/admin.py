from django.contrib import admin

from intempo.models import UserProfile, Album, Review, Comment

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'user', 'profile_picture','join_date')

class AlbumAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'artist','creation_date','album_cover','description','tags')

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id','album','time_posted', 'review_text','rating','user')

class CommentAdmin(admin.ModelAdmin):
    list_display = ('id','time_posted', 'comment_text','user','review')

admin.site.register(UserProfile,UserProfileAdmin)
admin.site.register(Album,AlbumAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Comment,CommentAdmin)
