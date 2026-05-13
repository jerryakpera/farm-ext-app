"""
Forms for the visits app — crop analysis and related child forms.
"""

# django_packages
from django import forms

# app_packages
from ..models import VisitIssue


class VisitIssueForm(forms.ModelForm):
    """
    Captures a single general issue identified during a visit.

    Submitted individually from the visit detail page. One form
    submission creates one VisitIssue record. The visit FK is
    attached in the view before saving.
    """

    class Meta:
        model = VisitIssue
        fields = ["title", "severity", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 2}),
        }
        help_texts = {
            "title": "A short label for the issue (e.g. 'Standing water near crops').",
            "severity": "How serious this issue is.",
            "description": "Optional additional detail about the issue.",
        }
