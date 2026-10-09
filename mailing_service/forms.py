from django import forms
from django.db import transaction
from django.utils import timezone

from .models import Distribution, Message, Recipient


class DistributionForm(forms.ModelForm):
    class Meta:
        model = Distribution
        fields = ["start_time", "end_time", "message", "recipients"]
        widgets = {
            "start_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "end_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user is not None:
            self.fields["message"].queryset = Message.objects.filter(owner=user)

            self.fields["recipients"].queryset = Recipient.objects.filter(owner=user)


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["message_topic", "message_content"]


class RecipientForm(forms.ModelForm):
    class Meta:
        model = Recipient
        fields = ["name", "email", "comment"]

"""ниже форма для того, чтобы был ввод данных от на одной странице при создании рассылки"""

class DistributionWithMessageForm(forms.Form):
    # Поля модели Message
    message_topic = forms.CharField(
        label='Тема письма',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Например, Новости компании',
        }),
    )

    message_content = forms.CharField(
        label='Текст сообщения',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 6,
            'placeholder': 'Введите текст письма...',
        }),
    )

    # Поля модели Distribution
    start_time = forms.DateTimeField(
        label='Время начала',
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control',
        }),
        input_formats=['%Y-%m-%dT%H:%M'],
    )

    end_time = forms.DateTimeField(
        label='Время окончания',
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control',
        }),
        input_formats=['%Y-%m-%dT%H:%M'],
    )

    recipients = forms.ModelMultipleChoiceField(
        label='Получатели',
        queryset=Recipient.objects.none(),
        widget=forms.SelectMultiple(attrs={
            'class': 'form-select',
            'size': 5,
        }),
        error_messages={
            'required': 'Выберите хотя бы одного получателя.',
        },
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.user is not None:
            self.fields['recipients'].queryset = (
                Recipient.objects.filter(owner=self.user)
            )

    def clean(self):
        cleaned_data = super().clean()

        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if start_time and start_time < timezone.now():
            self.add_error(
                'start_time',
                'Время начала не может быть в прошлом.',
            )

        if start_time and end_time and end_time <= start_time:
            self.add_error(
                'end_time',
                'Время окончания должно быть позже времени начала.',
            )

        return cleaned_data

    @transaction.atomic
    def save(self, user):
        message = Message.objects.create(
            owner=user,
            message_topic=self.cleaned_data['message_topic'],
            message_content=self.cleaned_data['message_content'],
        )

        distribution = Distribution.objects.create(
            owner=user,
            message=message,
            start_time=self.cleaned_data['start_time'],
            end_time=self.cleaned_data['end_time'],
            status=Distribution.CREATED,
        )

        distribution.recipients.set(
            self.cleaned_data['recipients']
        )

        return distribution
