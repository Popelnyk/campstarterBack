from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models


class AppUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=50)
    name = models.CharField(max_length=50, null=True)
    email = models.EmailField(max_length=100, null=True)
    password = models.CharField(max_length=200)
    work = models.CharField(max_length=30, null=True)
    hometown = models.CharField(max_length=30, null=True)
    hobbies = models.CharField(max_length=30, null=True)

    #photo = models.ImageField(upload_to='uploads/')
    #bonuses


class Campaign(models.Model):
    owner = models.ForeignKey('auth.User', related_name='campaigns', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, unique=True)
    about = models.TextField(max_length=1500)
    youtube_link = models.URLField(max_length=50)
    goal_amount_of_money = models.PositiveIntegerField()
    current_amount_of_money = models.PositiveIntegerField(default=0)
    creation_date = models.DateTimeField(auto_now_add=True)
    #bonuses

    class Meta:
        ordering = ['creation_date']


class Rating(models.Model):
    owner = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    value = models.PositiveSmallIntegerField()


class Comment(models.Model):
    owner = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    campaign = models.ForeignKey(Campaign, related_name='comments', on_delete=models.CASCADE)
    text = models.TextField(max_length=200)
    creation_date = models.DateTimeField(auto_now_add=True)
    count_of_likes = models.PositiveIntegerField(default=0)


class Like(models.Model):
    owner = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, related_name='likes', on_delete=models.CASCADE)


class New(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    about = models.TextField(max_length=1000)
    creation_date = models.DateTimeField(auto_now_add=True)


class Tag(models.Model):
    pass


class Type(models.Model):
    pass
