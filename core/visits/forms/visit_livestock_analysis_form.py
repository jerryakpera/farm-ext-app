"""
Forms for the visits app — livestock analysis, media, follow-up, and farmer feedback.
"""

# django_packages
from django import forms

# other_apps_packages
from core.farms.models import Animal

# app_packages
from ..models import VisitLivestockAnalysis


class VisitLivestockAnalysisForm(forms.ModelForm):
    """
    Records the condition and observations for a single livestock species
    during a visit.

    Submitted individually from the visit detail page. One form submission
    creates one VisitLivestockAnalysis record. The visit FK is attached in
    the view before saving.

    The animal queryset is scoped to animals registered on the visit's farm
    where possible, falling back to all animals when the visit has no farm
    or the farm has no animals registered yet.

    Parameters
    ----------
    *args
        Positional arguments passed to the parent form initialiser.
    visit : Visit or None
        When provided, limits the animal queryset to animals associated
        with the visit's farm.
    **kwargs
        Keyword arguments passed to the parent form initialiser.
    """

    class Meta:
        model = VisitLivestockAnalysis
        fields = [
            "animal",
            "breed_or_variety",
            "production_purpose",
            "housing_system",
            "total_population",
            "number_sick",
            "number_dead_this_period",
            "overall_condition",
            "body_condition_score",
            "feed_availability",
            "water_availability",
            "vaccination_status",
            "deworming_status",
            "ectoparasite_presence",
            "general_observations",
        ]
        widgets = {
            "general_observations": forms.Textarea(attrs={"rows": 3}),
            "feed_availability": forms.Textarea(attrs={"rows": 2}),
            "water_availability": forms.Textarea(attrs={"rows": 2}),
            "vaccination_status": forms.Textarea(attrs={"rows": 2}),
            "deworming_status": forms.Textarea(attrs={"rows": 2}),
        }
        help_texts = {
            "animal": "The livestock species being assessed.",
            "breed_or_variety": "Breed or local variety name, if known.",
            "production_purpose": "The primary reason this animal is kept on the farm.",
            "housing_system": "How the animals are housed or managed.",
            "total_population": "Approximate total number of this species on the farm.",
            "number_sick": "Number of animals showing signs of illness at time of visit.",
            "number_dead_this_period": (
                "Deaths recorded since the last visit or in the current period."
            ),
            "overall_condition": "Overall assessment of the herd or flock condition.",
            "body_condition_score": "Body condition score on a 1–5 scale, if assessed.",
            "feed_availability": "Description of the feed or fodder situation at time of visit.",
            "water_availability": "Description of water source availability and quality.",
            "vaccination_status": "Current vaccination status or last vaccination date, if known.",
            "deworming_status": "Last deworming date or treatment history, if known.",
            "ectoparasite_presence": (
                "Check if ticks, lice, mites, or other ectoparasites were observed."
            ),
            "general_observations": "General free-text observations about the livestock.",
        }
        labels = {
            "number_dead_this_period": "Deaths this period",
            "ectoparasite_presence": "Ectoparasites present",
            "body_condition_score": "Body condition score (1–5)",
        }

    def __init__(self, *args, visit=None, **kwargs):
        """
        Scope the animal queryset to the visit's farm where possible.

        Parameters
        ----------
        visit : Visit or None
            When provided, the animal queryset is filtered to animals
            linked to the farm being visited. Falls back to all animals
            when the visit is None or the farm has no animals registered.
        """

        super().__init__(*args, **kwargs)

        if visit is not None and visit.farm_id:
            farm_animals = visit.farm.animals.all()
            if farm_animals.exists():
                self.fields["animal"].queryset = farm_animals
            else:
                self.fields["animal"].queryset = Animal.objects.all()
        else:
            self.fields["animal"].queryset = Animal.objects.all()

        self.fields["animal"].empty_label = "— Select an animal —"
        self.fields["production_purpose"].required = False
        self.fields["housing_system"].required = False
        self.fields["overall_condition"].required = False
