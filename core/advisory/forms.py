"""
Forms for the advisory app.
"""

# django_packages
from django import forms

# app_packages
from .models import AdvisoryPost


class AdvisoryPostForm(forms.ModelForm):
    """
    ModelForm for creating and editing an advisory post.

    Parameters
    ----------
    *args : tuple
        Positional arguments passed to the base ModelForm.
    **kwargs : dict
        Keyword arguments passed to the base ModelForm.
    """

    # Declared outside Meta so it is a plain CharField, not a taggit widget.
    tags = forms.CharField(
        required=False,
        widget=forms.TextInput(),
        label="Tags",
        help_text="Comma-separated keywords, e.g. maize, pest control, irrigation.",
    )

    class Meta:
        model = AdvisoryPost
        fields = [
            "title",
            "post_type",
            "body",
            "cover_image",
            "video_url",
            "attachment",
            # "tags" is intentionally absent — handled by the field declared above.
        ]
        widgets = {
            "body": forms.Textarea(attrs={"rows": 8}),
        }
        labels = {
            "post_type": "Post type",
            "video_url": "Video URL",
            "cover_image": "Cover image",
        }
        help_texts = {
            "body": "Write the full content of your advisory post.",
            "video_url": "Paste a YouTube or Vimeo link if this post includes a video.",
            "attachment": "Upload a PDF guide or data sheet (optional).",
        }

    def __init__(self, *args, **kwargs):
        """
        Initialize the advisory post form.
        """

        super().__init__(*args, **kwargs)

        # Pre-populate the tags field when editing an existing instance.
        if self.instance and self.instance.pk:
            self.fields["tags"].initial = ", ".join(
                self.instance.tags.values_list("name", flat=True)
            )
