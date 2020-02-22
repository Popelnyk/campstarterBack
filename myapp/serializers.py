from rest_framework import serializers
from myapp.models import Campaign, New, Comment, Tag, Type, AppUser, Like, Rating
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
    #serializers.PrimaryKeyRelatedField(many=True, queryset=Campaign.objects.all(), allow_null=True)

    class Meta:
        model = AppUser
        fields = ['id', 'username', 'password', 'name', 'email', 'work', 'hometown', 'hobbies', 'campaigns']

    def create(self, validated_data):
        user = User.objects.create_user(username=validated_data.get('username'),
                                        email=validated_data.get('email'),
                                        password=validated_data.get('password'))

        return AppUser.objects.create(user=user, **validated_data)

    def get_campaigns(self, appuser):
        ids = []
        for item in Campaign.objects.filter(owner=appuser.user):
            ids.append(item.id)
        return ids

    '''
    def update(self, instance, validated_data):
        print(validated_data)
        print(type(instance))
        print(self.context)
        #instance.username = validated_data.get('username')
        #instance.email = validated_data.get('email')
        #instance.password = validated_data.get('password')
        #work = validated_data.get('work', instance.work)
        #hometown = validated_data.get('hometown', instance.hometown)
        #hobbies = validated_data.get('hobbies', instance.hobbies)
        #campaigns = validated_data.get('campaigns', instance.campaigns)

        instance.save()
        return instance
    '''


    '''
    def restore_object(self, attrs, instance=None):
        if instance is not None:
            instance.user.username = attrs.get('user.username', instance.user.username)
            instance.user.email = attrs.get('user.email', instance.user.email)
            instance.work = attrs.get('work', instance.work)
            instance.hometown = attrs.get('hometown', instance.hometown)
            instance.hobbies = attrs.get('hobbies', instance.hobbies)
            instance.campaigns = attrs.get('campaigns', instance.campaigns)
            instance.user.password = attrs.get('user.password', instance.user.password)
            return instance

        user = User.objects.create_user(username=attrs.get('user.username'), email=attrs.get('user.email'),
                                        password=attrs.get('user.password'))
        return AppUser(user=user)
    '''


class CampaignSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    total_rating = serializers.SerializerMethodField()

    class Meta:
        model = Campaign
        fields = ['id', 'owner', 'name', 'about', 'youtube_link',
                  'goal_amount_of_money', 'current_amount_of_money',
                  'creation_date', 'total_rating']


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

