"""Модель для приложения birthday."""
from birthday.validators import real_age
from django.db import models
from django.urls import reverse


class Birthday(models.Model):
    """Класс Birthday."""

    first_name = models.CharField('Имя', max_length=20)
    last_name = models.CharField(
        'Фамилия',
        blank=True,
        help_text='Необязательное поле',
        max_length=20,
    )
    birthday = models.DateField(
        'Дата рождения',
        validators=(real_age,)
    )
    image = models.ImageField(
        'Фото',
        upload_to='birthdays_images',
        blank=True
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('first_name', 'last_name', 'birthday'),
                name='Unique person constraint',
            ),
        )

    def __str__(self):
        return f'{self.first_name} - {self.last_name}'

    def get_absolute_url(self):
        # С помощью функции reverse() возвращаем URL объекта.
        return reverse('birthday:detail', kwargs={'pk': self.pk})
