"""
Forms for the visits app — livestock analysis, media, follow-up, and farmer feedback.
"""

# django_packages
from django import forms

# app_packages
from ..models import Visit


class VisitFollowUpForm(forms.ModelForm):
    """
    Records the follow-up plan and outcome at the end of a visit.

    ``follow_up_date`` is only required when ``follow_up_required`` is
    True. The template is responsible for toggling its visibility via
    JavaScript; this form enforces the constraint server-side in
    ``clean()``.

    When ``follow_up_required`` is False any value already stored in
    ``follow_up_date`` is cleared to prevent stale dates being retained.
    """

    class Meta:
        model = Visit
        fields = ["follow_up_required", "follow_up_date", "priority_level", "outcome"]
        widgets = {
            "follow_up_date": forms.DateInput(
                attrs={"type": "date"},
                format="%Y-%m-%d",
            ),
        }
        help_texts = {
            "follow_up_required": "Check if another visit to this farm is needed.",
            "follow_up_date": "The date the follow-up visit is scheduled for.",
            "priority_level": "How urgently the follow-up or identified issue needs attention.",
            "outcome": "The overall result or resolution of this visit.",
        }
        labels = {
            "follow_up_required": "Follow-up required",
            "follow_up_date": "Next visit date",
            "priority_level": "Priority level",
        }

    def clean(self):
        """
        Enforce that ``follow_up_date`` is provided when
        ``follow_up_required`` is True, and cleared when it is not.

        Returns
        -------
        dict
            The cleaned form data.
        """

        cleaned_data = super().clean()
        follow_up_required = cleaned_data.get("follow_up_required")
        follow_up_date = cleaned_data.get("follow_up_date")

        if follow_up_required and not follow_up_date:
            self.add_error(
                "follow_up_date",
                "Please provide the date for the follow-up visit.",
            )

        if not follow_up_required:
            cleaned_data["follow_up_date"] = None

        return cleaned_data
