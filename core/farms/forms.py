"""
Forms for the profiles app — used across the multi-step registration wizard.
"""

# django_packages
from django import forms

# other_apps_packages
from core.common.models import LGA

# app_packages
from .models import Crop


class CropCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    """
    Thin subclass of CheckboxSelectMultiple so templates can target this
    widget specifically with a dedicated CSS class rather than relying on
    generic widget detection.
    """

    def build_attrs(self, base_attrs, extra_attrs=None):
        """
        Add a CSS class to the wrapping element produced by the widget.

        Parameters
        ----------
        base_attrs : dict
            Base HTML attributes for the widget.
        extra_attrs : dict or None
            Additional attributes to merge in.

        Returns
        -------
        dict
            Merged attribute dictionary.
        """

        attrs = super().build_attrs(base_attrs, extra_attrs)
        attrs["class"] = attrs.get("class", "") + " crop-checkbox-group"

        return attrs


class FarmDetailsForm(forms.Form):
    """
    Step 3 — Farm and crop details. Collected for farmers only.

    primary_crop is a single FK-style choice (radio or select).
    other_crops is a many-to-many style multi-select rendered as
    a badge-style checkbox group.
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

    primary_crop = forms.ModelChoiceField(
        queryset=Crop.objects.all(),
        empty_label="— Select primary crop —",
        help_text="The main crop grown on this farm.",
    )

    other_crops = forms.ModelMultipleChoiceField(
        queryset=Crop.objects.all(),
        required=False,
        widget=CropCheckboxSelectMultiple,
        help_text="Select all additional crops grown on this farm.",
    )
