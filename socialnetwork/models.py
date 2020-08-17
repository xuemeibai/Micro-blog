from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
class Profile(models.Model):
    profile_picture = models.FileField(blank=True)
    content_type = models.CharField(max_length=50)
    bio_input_text = models.TextField(max_length=500, blank=True, null=True)
    following = models.ManyToManyField(User, related_name="user_following", blank = True)
    user = models.OneToOneField(User,on_delete=models.PROTECT)


class Post(models.Model):
    post_input_text = models.CharField(max_length=200)
    date_created = models.DateTimeField(default=timezone.now, blank=True)
    user = models.ForeignKey(User,on_delete=models.PROTECT)

    class Meta:
        ordering=['date_created']

class Comment(models.Model):
    user = models.ForeignKey(User,on_delete=models.PROTECT)
    comment_input_text = models.CharField(max_length = 200)
    date_created = models.DateTimeField(default=timezone.now, blank=True)
    post =models.ForeignKey(Post,on_delete=models.PROTECT)
    class Meta:
        ordering=['date_created']
