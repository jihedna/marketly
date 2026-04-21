"""Three-step strategy configuration form."""
from __future__ import annotations

from django import forms
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import CompanyProfile


class CompanyStepForm(forms.ModelForm):
    class Meta:
        model = CompanyProfile
        fields = ["name", "industry", "size", "website"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.required = name != "website"


OBJECTIVE_CHOICES = [
    ("awareness", _("Brand awareness")),
    ("leads", _("Lead generation")),
    ("conversion", _("Sales & conversions")),
    ("retention", _("Retention & loyalty")),
    ("launch", _("Product launch")),
]

BUDGET_CHOICES = [
    ("lt5k", _("Less than $5k/month")),
    ("5_25k", _("$5k – $25k/month")),
    ("25_100k", _("$25k – $100k/month")),
    ("gt100k", _("$100k+/month")),
]

DURATION_CHOICES = [
    ("4w", _("4 weeks")),
    ("3m", _("3 months")),
    ("6m", _("6 months")),
    ("12m", _("12 months")),
]


class CampaignStepForm(forms.Form):
    objective = forms.ChoiceField(choices=OBJECTIVE_CHOICES, label=_("Primary objective"))
    audience = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 3}),
        label=_("Target audience"),
        help_text=_("Demographics, interests, pains, channels they use."),
    )
    budget = forms.ChoiceField(choices=BUDGET_CHOICES, label=_("Budget range"))
    duration = forms.ChoiceField(choices=DURATION_CHOICES, label=_("Campaign duration"))
    challenges = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 3}),
        label=_("Current challenges"),
        required=False,
    )
