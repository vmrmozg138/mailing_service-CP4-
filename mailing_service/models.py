from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

# Create your models here.


class Recipient(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="recipients",
        verbose_name="Владелец",
    )
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    comment = models.TextField()

    def __str__(self):
        return f"{self.name} ({self.email})"


class Message(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="messages",
        verbose_name="Владелец",
    )
    message_topic = models.CharField(max_length=100)
    message_content = models.TextField()

    def __str__(self):
        return self.message_topic


class Distribution(models.Model):

    CREATED = "created"
    STARTED = "started"
    COMPLETED = "completed"

    STATUS_CHOICES = [
        (CREATED, "Создана"),
        (STARTED, "Запущена"),
        (COMPLETED, "Завершена"),
    ]

    start_time = models.DateTimeField(blank=False, null=False)
    end_time = models.DateTimeField(blank=False, null=False)
    status = models.CharField(
        choices=STATUS_CHOICES, max_length=100, verbose_name="Status"
    )
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    recipients = models.ManyToManyField(
        Recipient,
        verbose_name="Получатели",
        related_name="mailings",
        blank=True,
        help_text="Список клиентов, которые получат данную рассылку",
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="distributions",
        verbose_name="Владелец",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Активна",
    )

    def update_status(self):
        """обновление статуса"""
        now = timezone.now()

        if now < self.start_time:
            new_status = self.CREATED
        elif self.start_time <= now <= self.end_time:
            new_status = self.STARTED
        else:
            new_status = self.COMPLETED

        if new_status != self.status:
            self.status = new_status
            self.save(update_fields=["status"])

    def clean(self):
        super().clean()
        now = timezone.now()

        if self.start_time and self.start_time < now:
            raise ValidationError(
                {"start_time": "Время начала не может быть в прошлом"}
            )

        if self.start_time and self.end_time and self.end_time <= self.start_time:
            raise ValidationError(
                {"start_time": "Время начала должно быть раньше, чем время завершения"}
            )


class Distribution_Attempt(models.Model):

    SUCCEEDED = "succeeded"
    FAILED = "failed"

    STATUS_CHOICES = [(SUCCEEDED, "Успешно"), (FAILED, "Не успешно")]

    attempt_time = models.DateTimeField(blank=False, null=False)
    status = models.CharField(
        choices=STATUS_CHOICES, max_length=100, verbose_name="Статус"
    )
    server_response = models.TextField(blank=False, null=False)
    mailing = models.ForeignKey(
        Distribution,
        on_delete=models.CASCADE,
        related_name="attempts",
    )
    recipient = models.ForeignKey(
        Recipient,
        on_delete=models.CASCADE,
        related_name="attempts",
    )
