"""
Forms for the profiles app — used across the multi-step registration wizard.
"""

# django_packages
from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

# other_apps_packages
from core.common.models import LGA
from core.custom_user.models import User
from core.profiles.models import ExtensionAgentWhitelist


class RoleSelectionForm(forms.Form):
    """
    Step 1 — The user selects their role before any other fields are shown.
    """

    role = forms.ChoiceField(
        choices=[
            (User.Role.FARMER, "Farmer"),
            (User.Role.EXTENSION_AGENT, "Extension Agent"),
        ],
        widget=forms.RadioSelect,
        label="I am registering as a",
    )


class ProfileBioForm(forms.Form):
    """
    Step 2 — Collects profile credentials and biographical details.
    """

    # --- profile fields ---
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    email = forms.EmailField()
    phone_number = forms.CharField(max_length=20, required=False)
    password = forms.CharField(
        widget=forms.PasswordInput,
        validators=[validate_password],
    )
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    # --- farmer-only bio field ---
    lga = forms.ModelChoiceField(
        queryset=LGA.objects.all(),
        required=False,
        label="Local Government Area",
        help_text="The LGA where you are based.",
    )

    # --- agent-only bio fields ---
    agency_name = forms.CharField(
        max_length=255,
        required=False,
        help_text="e.g. ADP – Agricultural Development Programme",
    )
    staff_id = forms.CharField(
        max_length=50,
        required=False,
        label="Staff ID",
    )

    def clean_email(self):
        """
        For extension agent registrations, validate that the submitted email
        exists in the whitelist and has not already been used.

        The role value is injected onto the form instance by the wizard view's
        get_form() override before validation runs, so it is available here as
        self.selected_role.

        Returns
        -------
        str
            The cleaned, lowercased email address.

        Raises
        ------
        ValidationError
            If the email is not whitelisted or has already been used.
        """

        email = self.cleaned_data["email"].lower()
        role = getattr(self, "selected_role", None)

        if role == User.Role.EXTENSION_AGENT:
            try:
                entry = ExtensionAgentWhitelist.objects.get(email=email)
            except ExtensionAgentWhitelist.DoesNotExist:
                raise ValidationError(
                    "This email is not authorised for agent registration."
                )

            if entry.is_used:
                raise ValidationError("This email has already been used to register.")

        return email

    def clean(self):
        """
        Cross-field validation: confirm that the two password fields match.
        """

        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error("confirm_password", "Passwords do not match.")

        return cleaned_data


class FarmerProfileForm(forms.Form):
    """
    Allows a farmer to update their profile and the underlying User fields.

    Parameters
    ----------
    *args
        Positional arguments passed to the parent form class.
    user : User, optional
        The authenticated user whose fields are used to populate the form.
    profile : FarmerProfile, optional
        The farmer profile instance used to populate profile-specific fields.
    **kwargs
        Keyword arguments passed to the parent form class.
    """

    # --- user fields ---
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    phone_number = forms.CharField(max_length=20, required=False)
    profile_photo = forms.ImageField(required=False)

    # --- profile fields ---
    lga = forms.ModelChoiceField(
        queryset=LGA.objects.all(),
        required=False,
        label="Local Government Area",
    )
    address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
    )
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )

    def __init__(self, *args, user=None, profile=None, **kwargs):
        """
        Initialize the form with optional user and profile instances
        to prepopulate existing data.
        """

        super().__init__(*args, **kwargs)
        if user:
            self.fields["first_name"].initial = user.first_name
            self.fields["last_name"].initial = user.last_name
            self.fields["phone_number"].initial = user.phone_number
        if profile:
            self.fields["lga"].initial = profile.lga
            self.fields["address"].initial = profile.address
            self.fields["date_of_birth"].initial = profile.date_of_birth

    def save(self, user, profile):
        """
        Persist changes to both the User and FarmerProfile instances.

        Parameters
        ----------
        user : User
            The authenticated user whose fields will be updated.
        profile : FarmerProfile
            The farmer profile whose fields will be updated.
        """

        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.phone_number = self.cleaned_data["phone_number"]

        if self.cleaned_data.get("profile_photo"):
            user.profile_photo = self.cleaned_data["profile_photo"]

        user.save()

        profile.lga = self.cleaned_data["lga"]
        profile.address = self.cleaned_data["address"]
        profile.date_of_birth = self.cleaned_data["date_of_birth"]
        profile.save()
