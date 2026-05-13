"""
Forms for the visits app — crop analysis and related child forms.
"""

# django_packages
from django import forms

# app_packages
from ..models import VisitCropAnalysis


class VisitCropAnalysisForm(forms.ModelForm):
    """
    Records the condition and observations for a single crop during a visit.

    Submitted individually from the visit detail page. One form
    submission creates one VisitCropAnalysis record. The visit FK is
    attached in the view before saving.

    The crop and variety querysets are scoped to the crops registered
    on the visit's farm where possible, falling back to all crops when
    the visit has no farm or the farm has no crops registered yet.

    Parameters
    ----------
    *args
        Positional arguments passed to the parent form initialiser.
    visit : Visit or None
        When provided, limits the crop and variety querysets to crops
        associated with the visit's farm.
    **kwargs
        Keyword arguments passed to the parent form initialiser.
    """

    class Meta:
        model = VisitCropAnalysis
        fields = [
            "crop",
            "variety",
            "crop_stage",
            "date_planted",
            "expected_harvest_date",
            "crop_condition",
            "soil_moisture_status",
            "weed_presence",
            "rainfall_situation",
            "observations",
        ]
        widgets = {
            "date_planted": forms.DateInput(
                attrs={"type": "date"},
                format="%Y-%m-%d",
            ),
            "expected_harvest_date": forms.DateInput(
                attrs={"type": "date"},
                format="%Y-%m-%d",
            ),
            "rainfall_situation": forms.Textarea(attrs={"rows": 2}),
            "observations": forms.Textarea(attrs={"rows": 3}),
        }
        help_texts = {
            "crop": "The crop being assessed.",
            "variety": "The specific variety or strain, if known.",
            "crop_stage": "The current growth stage of the crop.",
            "date_planted": "The date this crop was planted (optional).",
            "expected_harvest_date": "The expected harvest date (optional).",
            "crop_condition": "Overall condition rating for this crop.",
            "soil_moisture_status": "Describe the soil moisture level observed.",
            "weed_presence": "Check if weeds were observed around this crop.",
            "rainfall_situation": "Describe the recent rainfall situation.",
            "observations": "General observations about this crop.",
        }
        labels = {
            "crop_condition": "Crop condition",
            "weed_presence": "Weeds present",
        }

    def __init__(self, *args, visit=None, **kwargs):
        """
        Scope the crop and variety querysets to the visit's farm where possible.

        Parameters
        ----------
        visit : Visit or None
            When provided, the crop queryset is filtered to crops linked
            to the farm being visited. Falls back to all crops when the
            visit is None or the farm has no crops registered.
        """

        super().__init__(*args, **kwargs)

        # other_apps_packages
        from core.farms.models import Crop, CropVariety

        if visit is not None and visit.farm_id:
            farm = visit.farm
            farm_crop_ids = list(
                filter(
                    None,
                    [farm.primary_crop_id]
                    + list(farm.other_crops.values_list("id", flat=True)),
                )
            )
            if farm_crop_ids:
                self.fields["crop"].queryset = Crop.objects.filter(id__in=farm_crop_ids)
                self.fields["variety"].queryset = CropVariety.objects.filter(
                    crop_id__in=farm_crop_ids
                )
            else:
                self.fields["crop"].queryset = Crop.objects.all()
                self.fields["variety"].queryset = CropVariety.objects.all()
        else:
            self.fields["crop"].queryset = Crop.objects.all()
            self.fields["variety"].queryset = CropVariety.objects.all()

        self.fields["variety"].required = False
        self.fields["variety"].empty_label = "— Unknown / Not specified —"
        self.fields["crop"].empty_label = "— Select a crop —"
        self.fields["crop_stage"].required = False
        self.fields["crop_condition"].required = False
