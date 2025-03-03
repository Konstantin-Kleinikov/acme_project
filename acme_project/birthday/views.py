"""Представления для приложения birthday."""
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)
from django.urls import reverse_lazy

# Импортируем класс BirthdayForm, чтобы создать экземпляр формы.
from .forms import BirthdayForm
from .models import Birthday
from .utils import calculate_birthday_countdown


# Создаем миксин.
# class BirthdayMixin:
#     model = Birthday
#     success_url = reverse_lazy('birthday:list')


# class BirthdayFormMixin:
#     form_class = BirthdayForm
#     template_name = 'birthday/birthday_form.html'


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
    # model = Birthday
    # Этот класс сам может создать форму на основе модели!
    # Нет необходимости отдельно создавать форму через ModelForm.
    # Указываем поля, которые должны быть в форме:
    # fields = '__all__'
    # form_class = BirthdayForm
    # Явным образом указываем шаблон
    # template_name = 'birthday/birthday_form.html'
    # Указываем namespace:name страницы, куда будет перенаправлен пользователь
    # после создания объекта:
    # success_url = reverse_lazy('birthday:list')
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


# def birthday(request, pk=None):
#     print(request.POST)  # Напечатаем параметры запроса.
#     # Если в запросе указан pk (если получен запрос на редактирование объекта):
#     if pk is not None:
#         # Получаем объект модели или выбрасываем 404 ошибку.
#         instance = get_object_or_404(Birthday, pk=pk)
#     # Если в запросе не указан pk
#     # (если получен запрос к странице создания записи):
#     else:
#         # Связывать форму с объектом не нужно, установим значение None.
#         instance = None
#     # Передаём в форму либо данные из запроса, либо None.
#     # В случае редактирования прикрепляем объект модели.
#     form = BirthdayForm(
#         request.POST or None,
#         files=request.FILES or None,
#         instance=instance
#     )
#     # Создаём словарь контекста сразу после инициализации формы.
#     context = {'form': form}
#     # Если данных валидны...
#     if form.is_valid():
#         # ...то считаем, сколько дней осталось до дня рождения.
#         # Пока функции для подсчёта дней нет — поставим pass:
#         form.save()
#         birthday_countdown = calculate_birthday_countdown(
#             # ...и передаём в неё дату из словаря cleaned_data.
#             form.cleaned_data['birthday']
#         )
#         # Обновляем словарь контекста: добавляем в него новый элемент.
#         context.update({'birthday_countdown': birthday_countdown})
#     # Указываем нужный шаблон и передаём в него словарь контекста.
#     return render(request, 'birthday/birthday_form.html', context)
#
#
# def birthday_list(request):
#     # Получаем все объекты модели Birthday из БД с сортировкой по id.
#     birthdays = Birthday.objects.order_by('id')
#     # Создаем объект пагинатора с количеством 10 записей на страницу.
#     paginator = Paginator(birthdays, 1)
#     # Получаем из запроса значение параметра page.
#     page_number = request.GET.get('page')
#     # Получаем запрошенную страницу пагинатора.
#     # Если параметра page нет в запросе или его значение не приводится к числу,
#     # вернётся первая страница.
#     page_obj = paginator.get_page(page_number)
#     # Вместо полного списка объектов передаём в контекст
#     # объект страницы пагинатора
#     # context = {'birthdays': birthdays}
#     context = {'page_obj': page_obj}
#     return render(request, 'birthday/birthday_list.html', context)
#
#
# def delete_birthday(request, pk):
#     # Получаем объект модели или выбрасываем 404 ошибку.
#     instance = get_object_or_404(Birthday, pk=pk)
#     # В форму передаём только объект модели;
#     # передавать в форму параметры запроса не нужно.
#     form = BirthdayForm(instance=instance)
#     context = {'form': form}
#     # Если был получен POST-запрос...
#     if request.method == 'POST':
#         # ...удаляем объект:
#         instance.delete()
#         # ...и переадресовываем пользователя на страницу со списком записей.
#         return redirect('birthday:list')
#     # Если был получен GET-запрос — отображаем форму.
#     return render(request, 'birthday/birthday_form.html', context)

# def edit_birthday(request, pk):
#     # Находим запрошенный объект для редактирования по первичному ключу
#     # или возвращаем 404 ошибку, если такого объекта нет.
#     instance = get_object_or_404(Birthday, pk=pk)
#     # Связываем форму с найденным объектом: передаём его в аргумент instance.
#     form = BirthdayForm(request.POST or None, instance=instance)
#     context = {'form': form}
#     # Сохраняем данные, полученные из формы, и отправляем ответ:
#     if form.is_valid():
#         form.save()
#         birthday_countdown = calculate_birthday_countdown(
#             form.cleaned_data['birthday']
#         )
#         context.update({'birthday_countdown': birthday_countdown})
#     return render(request, 'birthday/birthday_form.html', context)
