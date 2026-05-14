"""
Filter classes for the farms app.
"""

# django_packages
from django import forms
from django.db.models import Q

# third_party_packages
import django_filters

# other_apps_packages
from core.common.models import LGA, Ward

# app_packages
from .models import Animal, Crop, Farm


class FarmFilter(django_filters.FilterSet):
    """
    Filter set for filtering farms in the all farms list view.
    """

    search = django_filters.CharFilter(
        method="filter_search",
        label="Search",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Farm or farmer name",
                "class": "w-full rounded-lg border-gray-300 text-sm",
            }
        ),
    )

    lga = django_filters.ModelChoiceFilter(
        queryset=LGA.objects.order_by("name"),
        empty_label="All LGAs",
        widget=forms.Select(
            attrs={
                "class": "w-full rounded-lg border-gray-300 text-sm",
            }
        ),
    )

    ward = django_filters.ModelChoiceFilter(
        queryset=Ward.objects.order_by("name"),
        empty_label="All Wards",
        widget=forms.Select(
            attrs={
                "class": "w-full rounded-lg border-gray-300 text-sm",
            }
        ),
    )

    primary_crop = django_filters.ModelChoiceFilter(
        queryset=Crop.objects.order_by("name"),
        empty_label="All Crops",
        widget=forms.Select(
            attrs={
                "class": "w-full rounded-lg border-gray-300 text-sm",
            }
        ),
    )

    animals = django_filters.ModelChoiceFilter(
        queryset=Animal.objects.order_by("name"),
        empty_label="All Animals",
        widget=forms.Select(
            attrs={
                "class": "w-full rounded-lg border-gray-300 text-sm",
            }
        ),
    )

    is_verified = django_filters.ChoiceFilter(
        choices=(
            ("", "All"),
            ("true", "Verified"),
            ("false", "Pending"),
        ),
        method="filter_verified",
        widget=forms.Select(
            attrs={
                "class": "w-full rounded-lg border-gray-300 text-sm",
            }
        ),
    )

    class Meta:
        model = Farm

        fields = [
            "lga",
            "ward",
            "primary_crop",
            "animals",
        ]

    def filter_search(self, queryset, name, value):
        """
        Filter farms by farm name or farmer name.

        Parameters
        ----------
        queryset : QuerySet
            The queryset being filtered.
        name : str
            The filter field name.
        value : str
            The search value.

        Returns
        -------
        QuerySet
            The filtered queryset.
        """

        return queryset.filter(
            Q(name__icontains=value)
            | Q(farmer__user__first_name__icontains=value)
            | Q(farmer__user__last_name__icontains=value)
        )

    def filter_verified(self, queryset, name, value):
        """
        Filter farms by verification status.

        Parameters
        ----------
        queryset : QuerySet
            The queryset being filtered.
        name : str
            The filter field name.
        value : str
            The selected verification value.

        Returns
        -------
        QuerySet
            The filtered queryset.
        """

        if value == "true":
            return queryset.filter(is_verified=True)

        if value == "false":
            return queryset.filter(is_verified=False)

        return queryset
