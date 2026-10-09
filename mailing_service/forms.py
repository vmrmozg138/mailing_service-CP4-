from django import forms

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
