"""
Forms for the visits app — livestock analysis, media, follow-up, and farmer feedback.
"""

# django_packages
from django import forms

# app_packages
from ..models import LivestockAction


class LivestockActionForm(forms.ModelForm):
    """
    Captures a single recommended intervention for a livestock species
    during a visit.

    Submitted individually from the livestock analysis detail page. One
    form submission creates one LivestockAction record. The analysis FK
    is attached in the view before saving.
    """

    class Meta:
        model = LivestockAction
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
