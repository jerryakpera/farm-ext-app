"""
Forms for the visits app — crop analysis and related child forms.
"""

# django_packages
from django import forms

# app_packages
from ..models import CropIssue


class CropIssueForm(forms.ModelForm):
    """
    Captures a single crop-specific problem within a crop analysis.

    Submitted individually from the crop analysis detail page. One form
    submission creates one CropIssue record. The analysis FK is
    attached in the view before saving.
    """

    class Meta:
        model = CropIssue
        fields = ["issue_type", "notes"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 2}),
        }
        help_texts = {
            "issue_type": "The category of crop problem observed.",
            "notes": "Any additional detail about this issue.",
        }
        labels = {
            "issue_type": "Issue",
        }
