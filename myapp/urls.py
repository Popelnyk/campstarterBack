from django.conf.urls import url
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from campstarter import settings
from myapp import views
from django.contrib import admin

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from myapp.views import MySocialView, FileView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('campaigns/', views.CampaignList.as_view()),
    path('tags/<int:pk>/', views.CampaignListByTag.as_view()),
    path('tags/', views.TagList.as_view()),
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
    path('comments/<int:pk>/like/', views.AddLike.as_view()),
]


urlpatterns += [
    path('api-auth/', include('rest_framework.urls')),
    url(r'^api/login/', include('rest_social_auth.urls_jwt_pair')),
    url(r'^api/login-custom/$', MySocialView.as_view(), name='social_login'),
]

urlpatterns += [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

urlpatterns += [
    url(r'^upload-file/$', FileView.as_view(), name='file-upload'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
