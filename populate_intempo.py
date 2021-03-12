#!/usr/bin/env python
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'intempo_project.settings')


import django
django.setup()

from datetime import datetime
django.setup()
from django.contrib.auth.models import User
from intempo.models import Album, UserProfile, Review, Comment


def populate():

    Albumslist = [
    {'name': "What's Going on", 'artist':'Marvin Gaye', 'creation_date':datetime.now(), 'album_cover': os.path.join(os.path.dirname(__file__),"Cover_Art/0.jpg"),'description': "Marvin Gaye’s masterpiece began as a reaction to police brutality. In May 1969, Renaldo “Obie” Benson, the Four Tops’ bass singer, watched TV coverage of hundreds of club-wielding cops breaking up the People’s Park, a protest hub in Berkeley. Aghast at the violence, Benson began to write a song with Motown lyricist Al Cleveland, trying to capture the confusion and pain of the times. He knew he had something big in his nascent version of “What’s Going On,” but the rest of the Four Tops weren’t interested, and Benson’s efforts to get Joan Baez to record it didn’t work out, either.",'tags':'Motown, soul, R&B'},
    {'name': "Pet Sounds", 'artist':'The Beach Boys', 'creation_date':datetime.now(), 'album_cover':os.path.join(os.path.dirname(__file__),"Cover_Art/1.jpg"),'description': "“Who’s gonna hear this shit?” Beach Boys singer Mike Love asked the band’s resident genius, Brian Wilson, in 1966, as Wilson played him the new songs he was working on. “The ears of a dog?” Confronted with his bandmate’s contempt, Wilson made lemonade of lemons. “Ironically,” he observed, “Mike’s barb inspired the album’s title.”",'tags' : 'Pop, Boy Band'},
    {'name': "Blue", 'artist':'Joni Mitchell', 'creation_date':datetime.now(), 'album_cover':os.path.join(os.path.dirname(__file__),"Cover_Art/2.jpg"),'description' :"In 1971, Joni Mitchell represented the West Coast feminine ideal — celebrated by Robert Plant as “a girl out there with love in her eyes and flowers in her hair” on Led Zeppelin’s “Goin’ to California.” It was a status that Mitchell hadn’t asked for and did not want: “I went, ‘Oh, my God, a lot of people are listening to me,’” she recalled in 2013. “’They better find out who they’re worshiping. Let’s see if they can take it. Let’s get real.’ So I wrote Blue.”",'tags':'folk music, pop, contemporary'},
    {'name': "Songs in the Key of Life", 'artist':'Stevie Wonder', 'creation_date':datetime.now(), 'album_cover':os.path.join(os.path.dirname(__file__),"Cover_Art/3.jpg"),'description' : "Months before the recording sessions for Songs in the Key of Life ended, the musicians in Stevie Wonder’s band had T-shirts made up that proclaimed, “We’re almost finished.” It was the stock answer to casual fans and Motown executives and everybody who’d fallen in love with Wonder’s early-Seventies gems – 1972’s Talking Book, 1973’s Innervisions, and 1974’s Fulfillingness’ First Finale – and who had been waiting two years for the next chapter. “I believed there was a lot that needed to be said,” Wonder said. More, in fact, than he could fit onto a double album – also included was a bonus EP, a seven-inch single with four more songs from the sessions.",'tags':'Motown, soul'},
    {'name': "Abbey Road", 'artist':'The Beatles', 'creation_date':datetime.now(), 'album_cover':os.path.join(os.path.dirname(__file__),"Cover_Art/4.jpg"),'description':"Abbey Road is the eleventh studio album by the English rock band the Beatles, released on 26 September 1969 by Apple Records.",'tags':'boy band, rock, pop'},
    {'name': "Nevermind", 'artist':'Nirvana', 'creation_date':datetime.now(), 'album_cover':os.path.join(os.path.dirname(__file__),"Cover_Art/5.jpg"),'description':"Nevermind is the second studio album by American rock band Nirvana, released on September 24, 1991 by DGC Records. Produced by Butch Vig, it was Nirvana's first release on the DGC label, as well as the first to feature drummer Dave Grohl.",'tags' : 'rock, 90s, masterpiece'},
    {'name': "Rumours", 'artist':'Fleetwood Mac', 'creation_date':datetime.now(), 'album_cover':os.path.join(os.path.dirname(__file__),"Cover_Art/6.jpg"),'description':"Rumours is the eleventh studio album by British-American rock band Fleetwood Mac, released on 4 February 1977 by Warner Bros. Records. Largely recorded in California in 1976, it was produced by the band with Ken Caillat and Richard Dashut.",'tags':'rock, 70s, masterpiece'},
    ]
    
    Userslist = [
    {'username':'MusicLover101', 'password':'password', 'profile_picture': (os.path.join(os.path.dirname(__file__),"profile_pictures/0.jpg")), 'join_date':datetime.now()},
    {'username':'PeterTheCritic', 'password':'password', 'profile_picture': (os.path.join(os.path.dirname(__file__),"profile_pictures/1.jpg")), 'join_date':datetime.now()},
    {'username':'LauraLovesMusic', 'password':'password', 'profile_picture': (os.path.join(os.path.dirname(__file__),"profile_pictures/2.jpg")), 'join_date':datetime.now()} ]
    
    Reviewslist = [
    {'time_posted':datetime.now(),'review_text':'Amazing my favourite album', 'rating':10.0,'user_id':UserProfile.getByUsername('MusicLover101'),'album_id': Album.objects.get_or_create(name = 'Blue')},
    {'time_posted':datetime.now(),'review_text':'Terrible album from a terrible band.AVOID!!!', 'rating':1.0,'user_id':UserProfile.getByUsername('PeterTheCritic'),'album_id': Album.objects.get_or_create(name = 'Pet Sounds')},
    {'time_posted':datetime.now(),'review_text':'Enjoyed this album quite a bit.','rating':5.0,'user_id':2,'album_id':1,'user_id':UserProfile.getByUsername('LauraLovesMusic'),'album_id': Album.objects.get_or_create(name = 'Pet Sounds')},
    {'time_posted':datetime.now(),'review_text':'Without a doubt the best album ever... if your and idiot!!', 'rating':2.0,'user_id':UserProfile.getByUsername('PeterTheCritic'),'album_id': Album.objects.get_or_create(name = 'Rumours')},
    {'time_posted':datetime.now(),'review_text':'Nice album, will listen to again.', 'rating':7.5,'user_id':UserProfile.getByUsername('LauraLovesMusic'),'album_id': Album.objects.get_or_create(name = 'Nevermind')}
    ]
    
    Commentslist = [
    {'time_posted':datetime.now(),'comment_text':"Wrong!! I am very smart and you are wrong!!",'user_id':UserProfile.getByUsername('MusicLover101'),'review_id': Review.objects.get_or_create(rating = 10.0)},
    {'time_posted':datetime.now(),'comment_text':"I love this album as well",'user_id':UserProfile.getByUsername('LauraLovesMusic'),'review_id': Review.objects.get_or_create(rating = 7.5)},
    {'time_posted':datetime.now(),'comment_text':"Sounds good. Will have a listen.",'user_id':UserProfile.getByUsername('PeterTheCritic'),'review_id': Review.objects.get_or_create(rating = 7.5)},
    {'time_posted':datetime.now(),'comment_text':"You hit it out of the park with this one.",'user_id':UserProfile.getByUsername('MusicLover101'),'review_id': Review.objects.get_or_create(rating = 1.0)},
    {'time_posted':datetime.now(),'comment_text':"Yawn.XD",'user_id':UserProfile.getByUsername('PeterTheCritic'),'review_id': Review.objects.get_or_create(rating = 10.0)},
    ]

    print("- Adding albums")
    for myAlbum in Albumslist:
        add_album(myAlbum)
    
    print("- Adding users")
    for myUser in Userslist:
        add_user(myUser)
    
    print("- Adding reviews")
    for myReview in Reviewslist:
        add_review(myReview)

    print("- Adding comments!")    
    for myComment in Commentslist:
        add_comment(myComment)
    
    print("Finished without any errors!")

def add_album(myAlbum):
    A = Album.objects.get_or_create(name=myAlbum['name'],artist=myAlbum['artist'],creation_date = myAlbum['creation_date'])[0]
    A.album_cover = myAlbum['album_cover']
    A.description = myAlbum['description']
    A.tags = myAlbum['tags']
    A.save()
    return A
    
def add_user(myUser):
    M = User.objects.get_or_create(username = myUser['username'])[0]
    U = UserProfile.objects.get_or_create(join_date = myUser['join_date'], user=M)[0]
    U.profile_picture = myUser['profile_picture']
    U.password = myUser['password']
    U.save()
    return U
    
def add_review(myReview):
    R = Review.objects.get_or_create(user=myReview['user_id'],album=myReview['album_id'][0],rating = myReview['rating'],time_posted = myReview['time_posted'])[0]
    ##all need to be added at the same time since they are required to be NOT NULL
    
    R.review_text = myReview['review_text']
    R.save()
    return R
    
def add_comment(myComment):
    C = Comment.objects.get_or_create(time_posted=myComment['time_posted'],user=myComment['user_id'],review= myComment['review_id'][0])[0]
    C.comment_text= myComment['comment_text']
    C.save()
    return C
    
    

    
if __name__ == '__main__':
    print('Starting Intempo population script...')
    populate()
    