from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.utils import timezone

from .models import Distribution, Distribution_Attempt


def send_mail(distribution: Distribution) -> dict:
    if not distribution.is_active:
        raise ValidationError("Рассылка отключена и не может быть отправлена")

    now = timezone.now()

    if not (distribution.start_time <= now <= distribution.end_time):
        raise ValidationError(
            f"Отправку невозможно выполнить сейчас. Разрешенный "
            f"период - между {distribution.start_time} и {distribution.end_time}"
        )

    recipients = distribution.recipients.all()
    if not recipients.exists():
        raise ValidationError("У данной рассылки нет получателей")

    message = distribution.message
    results = {
        "success_count": 0,
        "failed_count": 0,
        "errors": [],
    }

    for recipient in recipients:
        try:
            send_mail(
                subject=message.message_topic,
                message=message.message_content,
                from_email=None,
                recipient_list=[recipient.email],
                fail_silently=False,
            )

            Distribution_Attempt.objects.create(
                mailing=distribution,
                recipient=recipient,
                attempt_time=timezone.now(),
                status=Distribution_Attempt.SUCCEEDED,
                server_response="OK",
            )
            results["success_count"] += 1
        except Exception as e:
            error_text = str(e)
            Distribution_Attempt.objects.create(
                mailing=distribution,
                recipient=recipient,
                attempt_time=timezone.now(),
                status=Distribution_Attempt.FAILED,
                server_response=error_text,
            )
            results["failed_count"] += 1
            results["errors"].append(f"{recipient.email}: {error_text}")
            """logger.error(
                'Ошибка отправки mailing=%s → %s: %s',
                distribution.pk, recipient.email, error_text,
            )"""

        return results
