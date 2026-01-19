# cards/views.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from .models import Card
from .forms import CardForm


class CardListView(LoginRequiredMixin, ListView):
    model = Card
    template_name = 'cards/card_list.html'
    context_object_name = 'object_list'

    def get_queryset(self):
        return Card.objects.filter(user=self.request.user).order_by('-created_at')


class CardDetailView(LoginRequiredMixin, DetailView):
    model = Card
    template_name = 'cards/card_detail.html'

    def get_queryset(self):
        return Card.objects.filter(user=self.request.user)


class CardCreateView(LoginRequiredMixin, CreateView):
    model = Card
    form_class = CardForm
    template_name = 'cards/card_form.html'
    success_url = reverse_lazy('cards:card_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Карта успешно добавлена!')
        return super().form_valid(form)


class CardUpdateView(LoginRequiredMixin, UpdateView):
    model = Card
    form_class = CardForm
    template_name = 'cards/card_form.html'
    success_url = reverse_lazy('cards:card_list')

    def get_queryset(self):
        return Card.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Карта успешно обновлена!')
        return super().form_valid(form)


class CardDeleteView(LoginRequiredMixin, DeleteView):
    model = Card
    template_name = 'cards/card_confirm_delete.html'
    success_url = reverse_lazy('cards:card_list')

    def get_queryset(self):
        return Card.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Карта успешно удалена!')
        return super().delete(request, *args, **kwargs)