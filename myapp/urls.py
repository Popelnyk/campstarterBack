from django.urls import path, include
from rest_framework.routers import DefaultRouter

from myapp import views
from django.contrib import admin

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('campaigns/', views.CampaignList.as_view()),
    path('campaigns_by_tags/', views.CampaignListByTags.as_view()),
    path('campaigns/best/', views.BestCampaign.as_view()),
    path('campaigns/<int:pk>/', views.CampaignDetail.as_view()),
    path('users/', views.AppUserList.as_view()),
    path('users/<int:pk>/', views.AppUserDetail.as_view()),
    path('users/<int:pk>/campaigns/', views.CampaignListOfUser.as_view()),
    path('campaigns/<int:pk>/comments/', views.CommentList.as_view()),
    path('campaigns/<int:pk>/news/', views.NewList.as_view()),
    path('campaigns/<int:pk>/news/create-new/', views.NewCreate.as_view()),
    path('campaigns/<int:pk>/rating/', views.AddRating.as_view()),
    path('campaigns/<int:pk>/donate/', views.add_money),
    path('comments/<int:pk>/', views.CommentDetail.as_view()),
    path('comments/<int:pk>/like/', views.AddLike.as_view())
]


urlpatterns += [
    path('api-auth/', include('rest_framework.urls')),
]


urlpatterns += [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]