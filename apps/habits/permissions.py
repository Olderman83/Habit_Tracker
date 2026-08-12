from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.owner == request.user


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsPublicReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Разрешить чтение публичных привычек всем
        if request.method in SAFE_METHODS and obj.is_public:
            return True
        # Разрешить полный доступ только владельцу
        return obj.owner == request.user
