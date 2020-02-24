from django.http import HttpResponse
from django.middleware import csrf
from django.shortcuts import get_object_or_404
from requests import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.utils import json

from myapp.models import Campaign, New, Comment, Type, Tag, Like, Rating, AppUser, Bonus
from myapp.permissions import IsOwnerOrReadOnly, IsOwnerOfCampaignOrReadOnly
from myapp.serializers import CommentSerializer, CampaignSerializer, NewSerializer, AppUserSerializer, LikeSerializer, \
    RatingSerializer
from rest_framework import generics, filters, viewsets
from rest_framework import permissions
from django.contrib.auth.models import User


class AppUserList(generics.ListCreateAPIView):
    queryset = AppUser.objects.all()
    serializer_class = AppUserSerializer


class AppUserDetail(generics.RetrieveUpdateAPIView):
    queryset = AppUser.objects.all()
    serializer_class = AppUserSerializer


class CampaignList(generics.ListCreateAPIView):
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user, current_amount_of_money=0)

    search_fields = ['about', 'name', 'theme']
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Campaign.objects.all()
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
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly]
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer


class BestCampaign(generics.ListAPIView):

    def get_queryset(self):
        best_rating, rating = None, -1
        for item in Rating.objects.all():
            if item.value > rating:
                rating = item.value
                best_rating = item
        return Campaign.objects.filter(id=best_rating.campaign_id)

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
            return HttpResponse(status=500, content='not enough money on account')

        user.money = cur_user_money - value
        campaign.current_amount_of_money = cur_money + value

        for item in Bonus.objects.all():
            print(item.campaign_id)

        bonuses_of_campaign = Bonus.objects.filter(campaign=campaign)
        print(bonuses_of_campaign)

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
