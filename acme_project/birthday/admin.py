"""Модуль для администрирования приложения birthday."""
from django.contrib import admin

from .models import Birthday

admin.site.register(Birthday)
