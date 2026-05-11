"""
Forms for the profiles app — used across the multi-step registration wizard.
"""

# django_packages
from django import forms

# other_apps_packages
from core.common.models import LGA, Ward

# app_packages
from .models import Animal, Crop, Farm


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


class AnimalCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
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
        attrs["class"] = attrs.get("class", "") + " animal-checkbox-group"

        return attrs


class FarmDetailsForm(forms.Form):
    """
    Step 3 — Farm and crop details. Collected for farmers only.

    Parameters
    ----------
    *args
        Positional arguments passed to the parent form initialiser.
    farm : Farm or None
        When provided, the form fields are initialised from this instance
        so the edit view renders a pre-filled form.
    **kwargs
        Keyword arguments passed to the parent form initialiser.
    """

    farm_name = forms.CharField(max_length=255)

    farm_lga = forms.ModelChoiceField(
        queryset=LGA.objects.all(),
        label="Farm LGA",
        help_text="The LGA where the farm is located.",
    )

    farm_ward = forms.ModelChoiceField(
        queryset=Ward.objects.all(),
        label="Farm Ward",
        required=False,
        help_text="The ward within the selected LGA.",
    )

    farm_address = forms.CharField(
        label="Farm location",
        widget=forms.Textarea(attrs={"rows": 3}),
        help_text="Street address or description of the farm's location.",
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

    animals = forms.ModelMultipleChoiceField(
        queryset=Animal.objects.all(),
        required=False,
        widget=AnimalCheckboxSelectMultiple,
        help_text="Select all animals or livestock kept on this farm.",
    )

    def __init__(self, *args, farm=None, **kwargs):
        """
        Pre-populate fields when an existing Farm instance is supplied.

        Parameters
        ----------
        farm : Farm or None
            When provided, the form fields are initialised from this instance
            so the edit view renders a pre-filled form.
        """

        super().__init__(*args, **kwargs)

        if farm is not None:
            self.fields["farm_name"].initial = farm.name
            self.fields["farm_lga"].initial = farm.lga
            self.fields["farm_ward"].initial = farm.ward
            self.fields["farm_address"].initial = farm.address
            self.fields["size"].initial = farm.size
            self.fields["primary_crop"].initial = farm.primary_crop
            self.fields["other_crops"].initial = farm.other_crops.all()
            self.fields["animals"].initial = farm.animals.all()

            # Restore queryset so the saved ward is a valid choice on edit.
            if farm.lga_id:
                self.fields["farm_ward"].queryset = Ward.objects.filter(
                    lga_id=farm.lga_id
                )

        # On POST: widen the queryset to the submitted LGA so validation passes.
        elif args and (lga_id := args[0].get("farm_lga")):
            self.fields["farm_ward"].queryset = Ward.objects.filter(lga_id=lga_id)

    def save(self, farmer, farm=None):
        """
        Persist the validated form data to the database.

        Creates a new Farm when no `farm` instance is passed, or updates
        the existing one when it is.

        Parameters
        ----------
        farmer : FarmerProfile
            The profile of the farmer who owns this farm.
        farm : Farm or None
            When provided the existing instance is updated; otherwise a new
            Farm is created.

        Returns
        -------
        Farm
            The created or updated Farm instance.
        """
        data = self.cleaned_data

        if farm is None:
            farm = Farm(farmer=farmer)

        farm.name = data["farm_name"]
        farm.lga = data["farm_lga"]
        farm.ward = data.get("farm_ward")
        farm.address = data["farm_address"]
        farm.size = data["size"]
        farm.primary_crop = data["primary_crop"]

        if data.get("image"):
            farm.image = data["image"]

        farm.save()

        farm.other_crops.set(data["other_crops"])
        farm.animals.set(data["animals"])

        return farm


class FarmImageUploadForm(forms.Form):
    """
    Accepts a single image for a given farm.
    """

    image = forms.ImageField(
        help_text="Upload an image of your farm.",
    )
