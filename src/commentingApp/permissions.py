from rest_framework.permissions import BasePermission


class CustomerPermission(BasePermission):
    def has_permission(self, request, view):
        print(request.user)
        return True