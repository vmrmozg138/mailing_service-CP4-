from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import CreateView, ListView, TemplateView, FormView

from .forms import DistributionForm, MessageForm, RecipientForm, DistributionWithMessageForm
from .mixins import ManagerRequiredMixin
from .models import Distribution, Distribution_Attempt, Message, Recipient

"""переменная вне класса"""
User = get_user_model()


class MainPageView(TemplateView):
    template_name = "mailing_service/main_page.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()

        context["total_distributions"] = Distribution.objects.count()

        context["active_distributions"] = Distribution.objects.filter(
            start_time__lte=now,
            end_time__gte=now,
            status=Distribution.STARTED,
        ).count()

        context["unique_recipients"] = Recipient.objects.count()

        return context


class DistrbutionCreateView(LoginRequiredMixin, FormView):
    template_name = 'mailing_service/create_distribution.html'
    form_class = DistributionWithMessageForm
    success_url = reverse_lazy('mailing_service:distributions')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save(user=self.request.user)
        return super().form_valid(form)


class DistributionListView(LoginRequiredMixin, ListView):
    template_name = "mailing_service/distribution_list.html"
    model = Distribution
    context_object_name = "distributions"

    def get_queryset(self):
        queryset = Distribution.objects.annotate(
            successful_attempts=Count(
                "attempts", filter=Q(attempts__status=Distribution_Attempt.SUCCEEDED)
            ),
            failed_attempts=Count(
                "attempts", filter=Q(attempts__status=Distribution_Attempt.FAILED)
            ),
            total_attempts=Count("attempts"),
        )

        if self.request.user.is_manager:
            return queryset

        return queryset.filter(owner=self.request.user)


"""Сообщения"""


class MessageCreateView(LoginRequiredMixin, CreateView):
    template_name = "mailing_service/create_message.html"
    model = Message
    form_class = MessageForm

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


"""Получатели"""


class RecipientCreateView(LoginRequiredMixin, CreateView):
    template_name = "mailing_service/create_recipient.html"
    model = Recipient
    form_class = RecipientForm

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class RecipientListView(LoginRequiredMixin, ListView):
    template_name = "mailing_service/recipient_list.html"
    model = Recipient
    context_object_name = "recipients"

    def get_queryset(self):
        if self.request.user.is_manager:
            return Recipient.objects.all()

        return Recipient.objects.filter(owner=self.request.user)


"""Статистика"""


class StatisticsView(LoginRequiredMixin, TemplateView):
    template_name = "mailing_service/statistics.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        cache_key = f"statistics_user_{self.request.user.id}"

        stats = cache.get(cache_key)

        if stats is None:
            stats = Distribution_Attempt.objects.filter(
                mailing__owner=self.request.user
            ).aggregate(
                successful=Count("id", filter=Q(status=Distribution_Attempt.SUCCEEDED)),
                failed=Count("id", filter=Q(status=Distribution_Attempt.FAILED)),
            )

            cache.set(cache_key, stats, timeout=300)

        context["stats"] = stats

        return context


"""специальный контроллер для менеджера - просмотр пользователей"""


class UserListView(LoginRequiredMixin, ManagerRequiredMixin, ListView):

    template_name = "mailing_service/user_list.html"
    model = User
    context_object_name = "users"


class UserBlockView(LoginRequiredMixin, ManagerRequiredMixin, View):
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)

        user.is_active = False
        user.save(update_fields=["is_active"])

        return redirect("mailing_service:user_list")


class DisableDistributionView(LoginRequiredMixin, ManagerRequiredMixin, View):
    def post(self, request, pk):
        distribution = get_object_or_404(Distribution, pk=pk)

        distribution.is_active = False
        distribution.save(update_fields=["is_active"])

        return redirect("mailing_service:distributions")


"""страничка about - закешированная"""


@method_decorator(cache_page(60 * 15), name="dispatch")
class AboutView(TemplateView):
    template_name = "mailing_service/about.html"
