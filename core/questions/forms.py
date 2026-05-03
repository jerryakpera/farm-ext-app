"""
Forms for the questions app.
"""

# django_packages
from django import forms

# other_apps_packages
from core.farms.models import Crop, Farm

# app_packages
from .models import Question


class AskQuestionForm(forms.ModelForm):
    """
    ModelForm for a farmer to submit a new question.

    Parameters
    ----------
    *args
        Positional arguments passed to the parent form initialiser.
    farmer : FarmerProfile or None
        When provided, limits the farm queryset to farms owned by this farmer.
    **kwargs
        Keyword arguments passed to the parent form initialiser.
    """

    class Meta:
        model = Question
        fields = [
            "title",
            "body",
            "crop_concern",
            "farm",
            "image",
        ]
        widgets = {
            "body": forms.Textarea(attrs={"rows": 5}),
        }
        help_texts = {
            "title": "A short, descriptive title for your question.",
            "body": "Describe the problem or question in as much detail as possible.",
            "farm": "Link this question to one of your farms (optional).",
            "image": "An optional image to help illustrate the question.",
        }
        labels = {
            "body": "Details",
            "crop_concern": "Crop concern",
        }

    def __init__(self, *args, farmer=None, **kwargs):
        """
        Scope the farm queryset to the given farmer's own farms.

        Parameters
        ----------
        farmer : FarmerProfile or None
            When provided, only this farmer's farms appear in the dropdown.
        """

        super().__init__(*args, **kwargs)

        self.fields["farm"].queryset = (
            Farm.objects.filter(farmer=farmer) if farmer else Farm.objects.none()
        )
        self.fields["farm"].empty_label = "— Not farm-specific —"
        self.fields["crop_concern"].queryset = Crop.objects.all()
        self.fields["crop_concern"].empty_label = "— Select a crop —"

    def save(self, farmer, commit=True):
        """
        Attach the farmer before saving, then persist any uploaded images.

        Parameters
        ----------
        farmer : FarmerProfile
            The profile of the farmer submitting the question.
        commit : bool
            Whether to call .save() on the instance (default True).

        Returns
        -------
        Question
            The newly created Question instance.
        """

        question = super().save(commit=False)
        question.farmer = farmer

        if commit:
            question.save()

        return question
