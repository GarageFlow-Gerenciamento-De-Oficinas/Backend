from django.db.models import QuerySet


class ActiveStatusFilterMixin:
    active_field = "is_active"

    def filter_by_active_status(self, queryset: QuerySet) -> QuerySet:
        show = self.request.query_params.get("show")

        if show is None:
            show = "active"
        else:
            show = show.lower()

        if show == "active":
            return queryset.filter(**{self.active_field: True})

        if show == "not_active":
            return queryset.filter(**{self.active_field: False})

        if show == "all":
            return queryset

        return queryset.none()