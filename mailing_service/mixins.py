from django.core.exceptions import PermissionDenied


class ManagerRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_manager:
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)
