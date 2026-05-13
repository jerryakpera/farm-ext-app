"""
Forms for the visits app — crop analysis and related child forms.
"""

# django_packages
from django import forms

# app_packages
from ..models import CropAction


class CropActionForm(forms.ModelForm):
    """
    Captures a single recommended action within a crop analysis.

    Submitted individually from the crop analysis detail page. One form
    submission creates one CropAction record. The analysis FK is
    attached in the view before saving.
    """

    class Meta:
        model = CropAction
        fields = ["action_type", "notes"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 2}),
        }
        help_texts = {
            "action_type": "The type of intervention recommended.",
            "notes": "Any additional instructions for carrying out this action.",
        }
        labels = {
            "action_type": "Action",
        }
