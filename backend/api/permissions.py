from rest_framework import permissions


class IsAuthorOrAdminOrJustReadingRecipe(permissions.BasePermission):
    """Разрешает модификацию рецепта только его владельцу или
    администратору. В противном случае доступ только к просмотру.
    """
    def has_permission(self, request, view):
        is_authenticated = request.user and request.user.is_authenticated
        return (request.method in permissions.SAFE_METHODS
                or is_authenticated)

    def has_object_permission(self, request, view, obj):
        is_authenticated = request.user and request.user.is_authenticated
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user
                or (is_authenticated and request.user.is_admin)
                )


class IsUserOrAdminOrJustReadingUserdata(permissions.BasePermission):
    """Разрешает модификацию информации о пользователе только его владельцу
    или администратору. В противном случае доступ только к просмотру.
    """

    def has_object_permission(self, request, view, obj):
        is_authenticated = request.user and request.user.is_authenticated
        return (request.method in permissions.SAFE_METHODS
                or obj.username == request.user
                or (is_authenticated and request.user.is_admin)
                )


class IsAdminOrReadOnly(permissions.BasePermission):
    """Разрешает доступ к запросам только администратору
    или суперпользователю. В противном случае доступ только для чтения.
    """

    def has_permission(self, request, view):
        is_authenticated = request.user and request.user.is_authenticated
        return (request.method in permissions.SAFE_METHODS
                or (is_authenticated and request.user.is_admin)
                )

    def has_object_permission(self, request, view, obj):
        is_authenticated = request.user and request.user.is_authenticated
        return (request.method in permissions.SAFE_METHODS
                or (is_authenticated and request.user.is_admin)
                )


class IsSuperUserOrAdmin(permissions.BasePermission):
    """Разрешает доступ к запросам только администратору
    или суперпользователю.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin
