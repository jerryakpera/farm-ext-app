"""
Forms for the visits app — livestock analysis, media, follow-up, and farmer feedback.
"""

# django_packages
from django import forms

# app_packages
from ..models import Visit


class VisitMediaForm(forms.ModelForm):
    """
    Handles photo and document uploads for a visit.

    Maps directly to the image and file fields already on the Visit
    model. Validators defined on the model fields are inherited
    automatically by the ModelForm and do not need to be re-declared.

    This form is submitted from the visit detail page as a standalone
    update — the agent does not need to re-enter basic visit information
    to attach or replace media.
    """

    class Meta:
        model = Visit
        fields = ["farm_photo", "pest_photo", "soil_photo", "attachment"]
        help_texts = {
            "farm_photo": "A general photo of the farm taken during the visit.",
            "pest_photo": "A photo showing any pests or disease signs observed.",
            "soil_photo": "A photo of the soil condition taken during the visit.",
            "attachment": "Any supporting documents or files related to the visit.",
        }
        labels = {
            "farm_photo": "Farm photo",
            "pest_photo": "Pest / disease photo",
            "soil_photo": "Soil photo",
            "attachment": "Supporting document",
        }
