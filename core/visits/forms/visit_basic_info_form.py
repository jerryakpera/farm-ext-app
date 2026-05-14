"""
Forms for the visits app — basic visit information.
"""

# django_packages
from django import forms

# other_apps_packages
from core.farms.models import Farm

# app_packages
from ..models import Visit


class VisitBasicInfoForm(forms.ModelForm):
    """
    Captures the core identifying information for a farm visit.

    The farm queryset is scoped to farms whose LGA falls within the
    logged-in agent's assigned LGAs, so an agent cannot log a visit
    against a farm outside their jurisdiction.

    The ``purpose_other`` field is hidden by default and made required
    only when ``purpose`` is set to ``OTHER``. The template is
    responsible for toggling its visibility via JavaScript; this form
    enforces the constraint server-side in ``clean()``.

    Parameters
    ----------
    *args
        Positional arguments passed to the parent form initialiser.
    agent : ExtensionAgentProfile
        The profile of the agent logging the visit. Used to scope the
        farm queryset to the agent's assigned LGAs.
    **kwargs
        Keyword arguments passed to the parent form initialiser.
    """

    class Meta:
        model = Visit
        fields = [
            "farm",
            "visit_date",
            "visit_time",
            "purpose",
            "purpose_other",
        ]
        widgets = {
            "visit_date": forms.DateInput(
                attrs={"type": "date"},
                format="%Y-%m-%d",
            ),
            "visit_time": forms.TimeInput(
                attrs={"type": "time"},
                format="%H:%M",
            ),
            "purpose_other": forms.TextInput(
                attrs={"placeholder": "Please describe the purpose of the visit."},
            ),
        }
        help_texts = {
            "farm": "Only farms within your assigned LGAs are listed.",
            "visit_date": "The date the visit took place.",
            "visit_time": "The time the visit started (optional).",
            "purpose": "Select the main reason for this visit.",
            "purpose_other": "Required when the purpose is set to 'Other'.",
        }
        labels = {
            "visit_date": "Date of visit",
            "visit_time": "Time of visit",
            "purpose_other": "Other purpose",
        }

    def __init__(self, *args, agent=None, **kwargs):
        """
        Scope the farm queryset to the given agent's assigned LGAs.

        Parameters
        ----------
        agent : ExtensionAgentProfile or None
            When provided, the farm queryset is filtered to farms whose
            LGA is in the agent's ``assigned_lgas`` M2M relation.
            When ``None``, no farms are shown as a safe fallback.
        """

        super().__init__(*args, **kwargs)

        if agent is not None:
            self.fields["farm"].queryset = Farm.objects.all()
        else:
            self.fields["farm"].queryset = Farm.objects.none()

        self.fields["farm"].empty_label = "— Select a farm —"

        # purpose_other is hidden until JavaScript reveals it when the
        # agent selects "Other". The field is not required at the widget
        # level; clean() enforces the conditional requirement.
        self.fields["purpose_other"].required = False

    def clean(self):
        """
        Enforce that ``purpose_other`` is provided when ``purpose``
        is set to ``OTHER``, and cleared when it is not.

        Returns
        -------
        dict
            The cleaned form data.
        """

        cleaned_data = super().clean()
        purpose = cleaned_data.get("purpose")
        purpose_other = cleaned_data.get("purpose_other", "").strip()

        if purpose == Visit.VisitPurpose.OTHER and not purpose_other:
            self.add_error(
                "purpose_other",
                "Please describe the purpose of the visit when 'Other' is selected.",
            )

        # Prevent stale text from being saved when a different purpose is chosen.
        if purpose != Visit.VisitPurpose.OTHER:
            cleaned_data["purpose_other"] = ""

        return cleaned_data
