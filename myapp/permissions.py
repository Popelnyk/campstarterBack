from rest_framework import permissions

from myapp.models import New, Campaign


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.owner == request.user


class IsOwnerOfUserOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.id == request.user.id


class IsOwnerOfCampaignOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        campaign_id = view.kwargs['pk']
        campaign = Campaign.objects.get(id=campaign_id)

        return campaign.owner == request.user
