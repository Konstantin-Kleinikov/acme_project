"""Представления для приложения birthday."""
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)

# Импортируем класс BirthdayForm, чтобы создать экземпляр формы.
from .forms import BirthdayForm, CongratulationForm
from .models import Birthday, Congratulation
from .utils import calculate_birthday_countdown


class BirthdayListView(ListView):
    # Указываем модель, с котором работает CBV...
    model = Birthday
    # ... сортировку, которая будет применена при выводе списка объектов:
    ordering = 'id'
    # ... и даже настройки пагинации:
    paginate_by = 3


class BirthdayDetailView(DetailView):
    model = Birthday

    def get_context_data(self, **kwargs):
        # Получаем словарь контекста
        context = super().get_context_data(**kwargs)
        # Добавляем в словарь новый ключ
        context['birthday_countdown'] = calculate_birthday_countdown(
            # Дату рождения берём из объекта в словаре контекста:
            self.object.birthday
        )
        # Записываем в переменную form пустой объект формы.
        context['form'] = CongratulationForm()
        # Запрашиваем все поздравления для выбранного дня рождения.
        context['congratulations'] = (
            # Дополнительно подгружаем авторов комментариев,
            # чтобы избежать множества запросов к БД.
            self.object.congratulations.select_related('author')
        )
        return context


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        # Получаем текущий объект
        object = self.get_object()
        # Метод вернёт True, если текущий пользователь является автором объекта.
        # Если пользователь - автор объекта, то тест будет пройден.
        # Если нет, то будет вызывана ошибка 403.
        return object.author == self.request.user


class BirthdayCreateView(LoginRequiredMixin, CreateView):
    model = Birthday
    form_class = BirthdayForm

    def form_valid(self, form):
        # Присвоить полю author объект пользователя из запроса.
        form.instance.author = self.request.user
        # Продолжить валидацию, описанную в форме.
        return super().form_valid(form)


class BirthdayDeleteView(OnlyAuthorMixin, DeleteView):
    model = Birthday
    # template_name = 'birthday/birthday_form.html'
    success_url = reverse_lazy('birthday:list')


class BirthdayUpdateView(OnlyAuthorMixin, UpdateView):
    model = Birthday
    form_class = BirthdayForm
    # form_class = BirthdayForm
    # template_name = 'birthday/birthday_form.html'
    # success_url = reverse_lazy('birthday:list')


@login_required
def simple_view(request):
    return HttpResponse('Страница для залогиненных пользователей!')


class CongratulationCreateView(LoginRequiredMixin, CreateView):
    birthday = None
    model = Congratulation
    form_class = CongratulationForm

    def dispatch(self, request, *args, **kwargs):
        self.birthday = get_object_or_404(Birthday, pk=self.kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.birthday = self.birthday
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('birthday:detail', kwargs={'pk': self.birthday.pk})

@login_required
def add_comment(request, pk):
    """Добавляет комментарий к объекту birthday."""
    # Получаем объект дня рождения или выбрасываем 404 ошибку.
    birthday = get_object_or_404(Birthday, pk=pk)
    # Функция должна обрабатывать только POST-запросы.
    form = CongratulationForm(request.POST)
    if form.is_valid():
        # Создаём объект поздравления, но не сохраняем его в БД.
        congratulation = form.save(commit=False)
        # В поле author передаём объект автора поздравления.
        congratulation.author = request.user
        # В поле birthday передаём объект дня рождения.
        congratulation.birthday = birthday
        # Сохраняем объект в БД.
        congratulation.save()
    # Перенаправляем пользователя назад, на страницу дня рождения.
    return redirect('birthday:detail', pk=pk)
