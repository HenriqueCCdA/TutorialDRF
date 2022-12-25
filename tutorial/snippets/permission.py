from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an objct to edit it.
    """

    def has_object_permission(self, request, view, obj):

        # Read permissions are allowed to any request
        # so we'll always allow GET, HEAD or OPTIONS request
        if request.method is permissions.SAFE_METHODS:
            return True

        # Write permission are only allowed to owner of the snippet
        return obj.owner == request.user
