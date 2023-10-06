from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from core.models import Film, List
from datetime import date
from PIL import Image

def validate_age(passed_date):
    min_age = 16

    today = date.today()
    diff = today.year - passed_date.year

    if diff < min_age:
        raise ValidationError(
            ("You must be %(min_age)s years or older."),
            params={'min_age': min_age},
            )

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=False)
    name = models.CharField(max_length=30, blank=False)
    profile_image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    cover_image = models.ImageField(upload_to='user_covers', blank=True)
    bio = models.TextField(blank=True, max_length=512)
    dob = models.DateField(blank=False, validators=[validate_age], null=True)
    watchlist = models.OneToOneField(List, on_delete=models.CASCADE, null=True)
    favourites = models.ManyToManyField(Film, through='FavLog', blank=True)
    following = models.ManyToManyField('self', through='FollowLog', blank=True)

    # def save(self, *args, **kwargs):
    #     self.watchlist = List.objects.create(user=self.user, title='Watchlist')
    #     super().save(*args, **kwargs)

    def doesFollow(self, followee):
        return self.following.filter(user=followee).exists()
    
    def getFollowersCount(self):
        return self.followee.count()
    
    def getFollowingCount(self):
        return self.following.count()
    
    def inWatchlist(self, film):
        if film in self.watchlist.films.all():
            return True
        else:
            return False
        
    def hasWatched(self,film):
        return self.user.log_set.filter(film=film).exists()

    def __str__(self):
        return f'@{self.user.username}'
    
class FollowLog(models.Model):
    follower = models.ForeignKey(Profile, related_name='follower', on_delete=models.CASCADE, blank=False)       # Elly 3amal follow
    followee = models.ForeignKey(Profile, related_name='followee', on_delete=models.CASCADE, blank=False)       # Elly et3amalo follow
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'@{ self.follower.user.username } followed @{ self.followee.user.username } on { self.date }'
    

class FavLog(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    film = models.ForeignKey(Film, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'@{self.profile.user.username}: {self.film.title}'