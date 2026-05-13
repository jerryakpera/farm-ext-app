"""
Forms for the visits app — livestock analysis, media, follow-up, and farmer feedback.
"""

# django_packages
from django import forms

# app_packages
from ..models import LivestockIssue


class LivestockIssueForm(forms.ModelForm):
    """
    Captures a single health or management problem identified in a
    livestock species during a visit.

    Submitted individually from the livestock analysis detail page. One
    form submission creates one LivestockIssue record. The analysis FK
    is attached in the view before saving.
    """

    class Meta:
        model = LivestockIssue
        fields = ["issue_type", "notes"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 2}),
        }
        help_texts = {
            "issue_type": "The category of livestock problem observed.",
            "notes": "Any additional detail about this issue.",
        }
        labels = {
            "issue_type": "Issue",
        }
