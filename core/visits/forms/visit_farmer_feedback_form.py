"""
Forms for the visits app — livestock analysis, media, follow-up, and farmer feedback.
"""

# django_packages
from django import forms

# app_packages
from ..models import VisitFarmerFeedback


class VisitFarmerFeedbackForm(forms.ModelForm):
    """
    Records the farmer's feedback at the end of a visit.

    ``farmer_satisfaction_rating`` is validated to be between 1 and 5
    inclusive. The model enforces this via database-level validators;
    this form enforces it at the form level so a clear error message
    is shown to the agent before any database call is made.
    """

    class Meta:
        model = VisitFarmerFeedback
        fields = [
            "advice_understood_by_farmer",
            "farmer_satisfaction_rating",
            "farmer_comments",
        ]
        widgets = {
            "farmer_comments": forms.Textarea(attrs={"rows": 3}),
        }
        help_texts = {
            "advice_understood_by_farmer": "Did the farmer understand the advice given?",
            "farmer_satisfaction_rating": (
                "Farmer's satisfaction with the visit, "
                "from 1 (very dissatisfied) to 5 (very satisfied)."
            ),
            "farmer_comments": "Any comments or concerns raised by the farmer.",
        }
        labels = {
            "advice_understood_by_farmer": "Farmer understood the advice",
            "farmer_satisfaction_rating": "Satisfaction rating (1–5)",
            "farmer_comments": "Farmer comments",
        }

    def clean_farmer_satisfaction_rating(self):
        """
        Validate that the satisfaction rating falls within the 1–5 range.

        Returns
        -------
        int or None
            The validated rating value, or None if the field was left blank.

        Raises
        ------
        ValidationError
            If the submitted value is outside the 1–5 range.
        """

        rating = self.cleaned_data.get("farmer_satisfaction_rating")

        if rating is not None and not (1 <= rating <= 5):
            raise forms.ValidationError("Satisfaction rating must be between 1 and 5.")

        return rating
