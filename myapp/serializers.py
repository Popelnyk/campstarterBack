from rest_framework import serializers
from rest_framework.utils import json

from myapp.models import Campaign, New, Comment, Tag, AppUser, Like, Rating, Bonus
from django.contrib.auth.models import User
from rest_framework import permissions
import rest_registration
from functools import reduce


'''
class UserSerializer(serializers.ModelSerializer):
    campaigns = serializers.PrimaryKeyRelatedField(many=True, queryset=Campaign.objects.all())

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'campaigns']
'''


class AppUserSerializer(serializers.ModelSerializer):
    campaigns = serializers.SerializerMethodField()
    bonuses = serializers.SerializerMethodField()

    class Meta:
        model = AppUser
        fields = ['id', 'username', 'password', 'name', 'email', 'work', 'hometown', 'hobbies', 'money', 'campaigns',
                  'bonuses']

    def create(self, validated_data):
        user = User.objects.create_user(id=validated_data.get('id'),
                                        username=validated_data.get('username'),
                                        email=validated_data.get('email'),
                                        password=validated_data.get('password'))

        return AppUser.objects.create(user=user, username=validated_data.get('username'),
                                      name=validated_data.get('name'), work=validated_data.get('work'),
                                      hometown=validated_data.get('hometown'), hobbies=validated_data.get('hobbies'))

    def get_campaigns(self, appuser):
        result = []
        for item in Campaign.objects.filter(owner=appuser.user):
            result.append({'id': item.id, 'name': item.name, 'about': item.about, 'creation_date': item.creation_date})
        return result

    def get_bonuses(self, appuser):
        result = []
        bonus_list = Bonus.objects.filter(owner__id=appuser.id)
        for item in bonus_list:
            result.append(item.about)
        return result


class CampaignSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    owner_id = serializers.ReadOnlyField(source='owner.id')
    total_rating = serializers.SerializerMethodField()
    bonuses = serializers.CharField(max_length=500, allow_null=True)
    tags = serializers.CharField(max_length=500, allow_null=True)

    class Meta:
        model = Campaign
        fields = ['id', 'owner', 'owner_id', 'name', 'theme', 'about', 'youtube_link',
                  'goal_amount_of_money', 'current_amount_of_money',
                  'creation_date', 'total_rating', 'bonuses', 'tags']

    def create(self, validated_data):
        campaign = Campaign.objects.create(**validated_data)
        bonuses_from_json = json.loads(validated_data.get('bonuses'))
        tags_from_json = json.loads(validated_data.get('tags'))
        print(bonuses_from_json)

        for item in bonuses_from_json:
            Bonus.objects.create(campaign=campaign, about=item['about'], value=int(item['value']))

        for item in tags_from_json:
            item['name'] = str.lower(item['name'])
            if Tag.objects.filter(name__exact=item['name']).count() > 0:
                tag = Tag.objects.get(name=item['name'])
                tag.campaign.add(campaign)
            else:
                Tag.objects.create(campaign=campaign, name=item['name'])

        return campaign

    def get_total_rating(self, campaign):
        sum_rating_list = Rating.objects.filter(campaign=campaign)
        sum_rating = 0
        for item in sum_rating_list:
            sum_rating += item.value
        count_of_ratings = Rating.objects.filter(campaign=campaign).count()
        if count_of_ratings == 0:
            count_of_ratings = 1
        return sum_rating / count_of_ratings


class RatingSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Rating
        fields = ['id', 'owner', 'value']


class CommentSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        creation_date = serializers.DateTimeField()
        fields = ['id', 'owner', 'text', 'campaign', 'creation_date', 'likes_count']

    def get_likes_count(self, comment):
        return Like.objects.filter(comment=comment).count()


class LikeSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Like
        fields = ['id', 'owner', 'comment']


class NewSerializer(serializers.ModelSerializer):
    class Meta:
        model = New
        creation_date = serializers.DateTimeField()
        fields = ['id', 'title', 'about', 'campaign', 'creation_date']

