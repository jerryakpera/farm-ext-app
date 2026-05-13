"""
Forms for the visits app — crop analysis and related child forms.
"""

# django_packages
from django import forms

# app_packages
from ..models import PestIncidence


class PestIncidenceForm(forms.ModelForm):
    """
    Captures a single pest occurrence within a crop analysis.

    Submitted individually from the crop analysis detail page. One form
    submission creates one PestIncidence record. The analysis FK is
    attached in the view before saving.
    """

    class Meta:
        model = PestIncidence
        fields = ["pest", "severity"]
        help_texts = {
            "pest": "The name of the pest observed (e.g. 'Fall Armyworm').",
            "severity": "How severe this pest infestation is.",
        }
