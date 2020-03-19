from django.contrib.auth import login
from django.http import HttpResponse
from django.middleware import csrf
from django.shortcuts import get_object_or_404
from httpie import status
from requests import Response, HTTPError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import FileUploadParser, MultiPartParser, FormParser
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.utils import json
from rest_framework.views import APIView
from rest_social_auth.views import *
from social_core.backends.oauth import BaseOAuth2
from social_core.exceptions import MissingBackend, AuthTokenError, AuthForbidden
from social_django.utils import load_strategy, load_backend

from myapp import serializers
from myapp.models import Campaign, New, Comment, Tag, Like, Rating, AppUser, Bonus, File
from myapp.permissions import IsOwnerOrReadOnly, IsOwnerOfCampaignOrReadOnly, IsOwnerOfUserOrReadOnly
from myapp.serializers import CommentSerializer, CampaignSerializer, NewSerializer, AppUserSerializer, LikeSerializer, \
    RatingSerializer, TagSerializer, MyUserSerializer, FileSerializer
from rest_framework import generics, filters, viewsets
from rest_framework import permissions
from django.contrib.auth.models import User


class MySocialView(SocialJWTPairUserAuthView):
    serializer_class = MyUserSerializer

    def perform_authentication(self, request):
        print(request.data)


class AppUserList(generics.ListCreateAPIView):

    queryset = AppUser.objects.all()
    serializer_class = AppUserSerializer


class AppUserDetail(generics.RetrieveUpdateAPIView):
    queryset = AppUser.objects.all()
    serializer_class = AppUserSerializer
    permission_classes = [IsOwnerOfUserOrReadOnly]


class CampaignList(generics.ListCreateAPIView):
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user, current_amount_of_money=0)

    search_fields = ['about', 'name', '=theme', 'tags']
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer


class CampaignListByTag(generics.ListAPIView):
    def get_queryset(self):
        tag_id = self.kwargs['pk']
        tag = Tag.objects.get(id=tag_id)
        print(tag)
        return Campaign.objects.filter(tag=tag)

    serializer_class = CampaignSerializer


class CampaignListOfUser(generics.ListCreateAPIView):
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user, current_amount_of_money=0)

    def get_queryset(self):
        user_id = self.kwargs['pk']
        user = User.objects.get(id=user_id)
        return Campaign.objects.filter(owner=user_id)

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = CampaignSerializer


class CampaignDetail(generics.RetrieveUpdateDestroyAPIView):

    def perform_destroy(self, instance):
        campaign = Campaign.objects.get(id=instance.id)
        tags_of_campaign = Tag.objects.filter(campaign=campaign)
        for tag in tags_of_campaign:
            if tag.campaign.count() == 1:
                tag.delete()

        bonuses_of_campaign = Bonus.objects.filter(campaign=campaign)
        for bonus in bonuses_of_campaign:
            bonus.delete()

        instance.delete()

    permission_classes = [permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly]
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer


class BestCampaign(generics.ListAPIView):

    def get_queryset(self):
        if Campaign.objects.count() > 0:
            best_rating, rating = None, -1
            for item in Rating.objects.all():
                if item.value > rating:
                    rating = item.value
                    best_rating = item
                    print(item.campaign_id, item.value)

            return Campaign.objects.filter(id=best_rating.campaign_id)
        return []

    serializer_class = CampaignSerializer


class AddRating(generics.CreateAPIView):
    def perform_create(self, serializer):
        campaign_id = self.kwargs['pk']
        campaign = Campaign.objects.get(id=campaign_id)
        ratings_of_user = Rating.objects.filter(owner=self.request.user)
        if len(ratings_of_user.filter(campaign=campaign)) == 0 and int(self.request.data['value']) <= 5:
            serializer.save(owner=self.request.user, campaign=campaign)
        else:
            raise Exception

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = RatingSerializer


class CommentList(generics.ListCreateAPIView):
    def perform_create(self, serializer):
        campaign_id = self.kwargs['pk']
        campaign = Campaign.objects.get(id=campaign_id)
        serializer.save(owner=self.request.user, campaign=campaign, count_of_likes=0)

    def get_queryset(self):
        camp = self.kwargs['pk']
        return Comment.objects.filter(campaign_id=camp)

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = CommentSerializer


class CommentDetail(generics.RetrieveDestroyAPIView):
    permission_classes = [IsOwnerOrReadOnly]
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer


class AddLike(generics.CreateAPIView):
    def perform_create(self, serializer):
        comment_id = self.kwargs['pk']
        comment = Comment.objects.get(id=comment_id)
        likes_of_user = Like.objects.filter(owner=self.request.user)
        if len(likes_of_user.filter(comment=comment)) == 0:
            serializer.save(owner=self.request.user, comment=comment)
        else:
            Like.objects.get(owner=self.request.user, comment=comment).delete()

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LikeSerializer


class NewList(generics.ListAPIView):
    def get_queryset(self):
        camp = self.kwargs['pk']
        return New.objects.filter(campaign_id=camp)

    #permission_classes = [IsOwnerOfCampaignOrReadOnly]
    serializer_class = NewSerializer


class NewCreate(generics.CreateAPIView):
    def perform_create(self, serializer):
        campaign_id = self.kwargs['pk']
        campaign = Campaign.objects.get(id=campaign_id)
        serializer.save(campaign=campaign)

    permission_classes = [IsOwnerOfCampaignOrReadOnly]
    serializer_class = NewSerializer


class TagList(generics.ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


#"{\"value\":13,\"campaign_id\":5,\"user_id\":1}"
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def add_money(request, pk):
    try:
        data = request.data
        print(data)
        campaign_id = int(data['campaign_id'])
        user_id = int(data['user_id'])
        value = int(data['value'])

        campaign = Campaign.objects.get(id=campaign_id)
        cur_money = campaign.current_amount_of_money
        user = AppUser.objects.get(id=user_id)
        cur_user_money = user.money

        if value > cur_user_money:
            return HttpResponse(status=400, content='not enough money on account')

        user.money = cur_user_money - value
        campaign.current_amount_of_money = cur_money + value
        bonuses_of_campaign = Bonus.objects.filter(campaign=campaign)

        for item in bonuses_of_campaign:
            print(item)
            if item.value <= value:
                item.owner.add(user)
                item.save()

        campaign.save()
        user.save()

        return HttpResponse(status=200, content='success')
    except Exception as e:
        return HttpResponse(status=500, content=e)


class FileView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        file_serializer = FileSerializer(data=request.data)
        file = request.data['file']
        campaign_id = int(request.data['campaign'])
        pos = int(request.data['position'])
        campaign = Campaign.objects.get(id=campaign_id)

        if file_serializer.is_valid():
            file_serializer.save(campaign=campaign, position=pos)
            return Response(file_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        pk = json.loads(request.body)['pk']
        campaign_id = json.loads(request.body)['campaignId']

        files = File.objects.filter(campaign_id=campaign_id)
        print(files)

        file = files.get(id=pk)
        file.delete()

        print(File.objects.filter(campaign_id=campaign_id))

        return Response(status=202)

