from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
# Create your models here.
######################################################################
## key word has to be write in capital for first letter of every word
#####################################################################

# define user profile mode, user profile include user inform related personal, for example titel picture, birthday, telephone number and so on.
class UserProfle(models.Model):
    # this line is required , links userprofile to user model instance
    user = models.OneToOneField(User)

    # define user profile fields, user homepage, user birthday, and user head photo, and activation key and expires time

    website = models.URLField(blank=True)
    birthday = models.DateField(blank=True)
    picture = models.ImageField(upload_to='profile_images', blank=True)
    activation_key = models.CharField(max_length=40, blank=True)
    key_expires = models.DateTimeField(default=datetime.today())

    # Override the __unicode__() method to return out something meanningful
    def __unicode__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = u'User profile'