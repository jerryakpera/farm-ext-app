"""
Forms for the profiles app — used across the multi-step registration wizard.
"""

# django_packages
from django import forms

# other_apps_packages
from core.common.models import LGA


class FarmDetailsForm(forms.Form):
    """
    Step 3 — Farm and crop details. Collected for farmers only.
    """

    farm_name = forms.CharField(max_length=255)
    farm_lga = forms.ModelChoiceField(
        queryset=LGA.objects.all(),
        label="Farm LGA",
        help_text="The LGA where the farm is located.",
    )
    farm_address = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 3}),
        help_text="Street address or description of the farm's location.",
    )
    landmark = forms.CharField(
        max_length=255,
        required=False,
        help_text="A nearby landmark to help locate the farm.",
    )
    size = forms.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text="Farm size in hectares.",
    )
    primary_crop = forms.CharField(
        max_length=100,
        help_text="e.g. Maize, Tomato, Yam.",
    )
    other_crops = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 2}),
        required=False,
        help_text="Comma-separated list of any other crops grown on the farm.",
    )
    latitude = forms.DecimalField(
        max_digits=9,
        decimal_places=6,
        required=False,
        help_text="Optional GPS latitude.",
    )
    longitude = forms.DecimalField(
        max_digits=9,
        decimal_places=6,
        required=False,
        help_text="Optional GPS longitude.",
    )
