"""
Forms for the visits app — livestock analysis, media, follow-up, and farmer feedback.
"""

# django_packages
from django import forms

# app_packages
from ..models import LivestockDiseaseIncidence


class LivestockDiseaseIncidenceForm(forms.ModelForm):
    """
    Captures a single disease or suspected condition observed in a
    livestock species during a visit.

    Submitted individually from the livestock analysis detail page. One
    form submission creates one LivestockDiseaseIncidence record. The
    analysis FK is attached in the view before saving.
    """

    class Meta:
        model = LivestockDiseaseIncidence
        fields = [
            "disease_name",
            "severity",
            "confidence_level",
            "symptoms_observed",
            "animals_affected_count",
        ]
        widgets = {
            "symptoms_observed": forms.Textarea(attrs={"rows": 2}),
        }
        help_texts = {
            "disease_name": "Name of the disease or condition observed or suspected.",
            "severity": "How severe this disease incidence is.",
            "confidence_level": "How certain you are about this diagnosis.",
            "symptoms_observed": "Clinical signs or symptoms noted in the affected animals.",
            "animals_affected_count": (
                "Estimated number of animals showing signs of this condition."
            ),
        }
        labels = {
            "confidence_level": "Diagnosis confidence",
            "animals_affected_count": "Animals affected",
        }
