from datetime import timedelta
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Decision, Option, Vote, Invitation, Team


class DecisionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['voters'].required = True
        self.fields['voters'].queryset = User.objects.filter(
            teams__in=self.user.teams.all(),
        ).distinct().order_by('first_name', 'last_name')
        self.fields['voters'].label_from_instance = self.label_from_instance

    @staticmethod
    def label_from_instance(obj):
        return obj.get_full_name()

    def clean_start(self):
        data = self.cleaned_data['start']
        if data < timezone.now():
            raise ValidationError("Der Zeitpunkt muss in der Zukunft liegen.", code='invalid')

        return data

    def clean_end(self):
        data = self.cleaned_data['end']
        if data < timezone.now():
            raise ValidationError("Der Zeitpunkt muss in der Zukunft liegen.", code='invalid')

        return data

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start')
        end = cleaned_data.get('end')

        diff = 15  # Minutes

        if start and end:
            if start + timedelta(minutes=diff) > end:
                raise ValidationError(
                    f"Die Dauer von Abstimmungen muss mind. {diff} Minuten betragen.",
                    code='invalid',
                )

    class Meta:
        model = Decision
        fields = ['subject', 'voters', 'start', 'end']
        labels = {
            'subject': "Gegenstand",
            'voters': "Stimmberechtigt",
            'start': "Beginn",
            'end': "Ende",
        }
        widgets = {
            'subject': forms.Textarea(attrs={
                'class': "textarea has-fixed-size",
                'placeholder': "Es sind maximal 255 Zeichen erlaubt.",
                'rows': 2,
            }),
            'voters': forms.SelectMultiple(attrs={
                'size': 6,
            }),
            'start': forms.DateTimeInput(attrs={
                'class': "input",
                'placeholder': "31.12.2099 16:30",
            }),
            'end': forms.DateTimeInput(attrs={
                'class': "input",
                'placeholder': "31.12.2099 16:45",
            }),
        }


class VoteForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.decision = kwargs.pop('decision')
        super().__init__(*args, **kwargs)
        self.fields['option'].queryset = Option.objects.filter(decision=self.decision)

    class Meta:
        model = Vote
        fields = ['option']
        widgets = {
            'option': forms.RadioSelect(attrs={
                'class': "radio",
            }),
        }


class InvitationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['teams'].queryset = Team.objects.filter(members__in=[self.user])

    def clean_expiry(self):
        data = self.cleaned_data['expiry']
        diff = data - timezone.now()
        value = round(diff.total_seconds() / 3600)
        if value not in [8, 24, 168]:
            raise ValidationError("Es können nur die vorgegebenen Fristen verwendet werden.", code='invalid')

        return data

    class Meta:
        model = Invitation
        fields = ['teams', 'expiry']
        labels = {
            'teams': "Organ(e)",
            'expiry': "Gültigkeit",
        }
        widgets = {
            'teams': forms.CheckboxSelectMultiple(),
            'expiry': forms.HiddenInput(),
        }
