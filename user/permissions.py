from rest_framework.permissions import BasePermission, SAFE_METHODS


class MyUserPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_anonymous:
            return request.method in SAFE_METHODS

        if view.basename in ["clients"]:
            if request.method in SAFE_METHODS:
                return True

            if request.method in ['POST']:
                return bool(request.user and request.user.is_authenticated)

            return bool(
                request.user and request.user.is_authenticated and (request.user.id == obj.id or request.user.is_staff))

        return False

    def has_permission(self, request, view):
        if view.basename in ["clients"]:
            if request.user.is_anonymous:
                return request.method in SAFE_METHODS

            return bool(request.user and request.user.is_authenticated)
        return False
