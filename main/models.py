from datetime import timedelta
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils.timezone import now, localtime


class CustomUser(AbstractUser):

    sex_s = (
        ('М', 'М'),
        ('Ж', 'Ж')
    )

    status_s = {
        ("Работаю", "Работаю"),
        ("Учащийся", "Учащийся",),
        ("Пенсионер", "Пенсионер"),
        ("Безработный", "Безработный"),
        ("Самозанятый", "Самозанятый"),
        ("Другое", "Другое")
    }

    patronymic = models.CharField(
        max_length=60, verbose_name='Отчество', null=True)
    hospital = models.CharField(
        max_length=350, verbose_name="Больница", null=True)
    section = models.CharField(
        max_length=200, verbose_name="Участок", null=True)
    phone = models.CharField(
        max_length=12, verbose_name="Контактный номер", null=True)
    iin = models.CharField(verbose_name="ИИН", max_length=12, null=True)
    sex = models.CharField(choices=sex_s, max_length=7,
                           verbose_name="Пол", help_text="Выберите пол", null=True)
    pcr = models.DateField(verbose_name="Дата ПЦР", null=True, blank=True)
    isVaccianted = models.BooleanField(
        verbose_name="Наличие вакцины", null=True)
    age = models.PositiveSmallIntegerField(verbose_name="Возраст", null=True)
    status = models.CharField(
        choices=status_s, max_length=17, verbose_name="Занятость", null=True)
    period = models.PositiveSmallIntegerField(default=0,
                                              verbose_name="Кол-во опросов", null=True)
    days = models.PositiveSmallIntegerField(
        default=10, verbose_name="Лимит опросов", null=True)

    def __str__(self):
        return f'{self.last_name} {self.first_name}'

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class Report(models.Model):
    GotPills_choices = {
        ("Да", "Да"),
        ("Нет", "Нет",),
        ("Не нуждаюсь", "Не нуждаюсь"),
    }
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Опрашиваемый")
    date_time = models.DateTimeField(
        default=now(), verbose_name="Дата и время опроса")
    high_temperature = models.BooleanField(
        verbose_name="Температура выше 37.0", default=False, null=True)
    runny_nose = models.BooleanField(
        verbose_name="Насморк", default=False, null=True)
    no_smell = models.BooleanField(
        verbose_name="Нет запахов", default=False, null=True)
    weakness = models.BooleanField(
        verbose_name="Слабость", default=False, null=True)
    muscle_pain = models.BooleanField(
        verbose_name="Боль в мышцах", default=False, null=True)
    nausea = models.BooleanField(
        verbose_name="Тошнота", default=False, null=True)
    cough = models.BooleanField(
        verbose_name="Кашель", default=False, null=True)
    dyspnea = models.BooleanField(
        verbose_name="Одышка", default=False, null=True)
    diarrhea = models.BooleanField(
        verbose_name="Диарея", default=False, null=True)
    vomiting = models.BooleanField(
        verbose_name="Рвота", default=False, null=True)
    isCalled = models.BooleanField(
        verbose_name="Звонил ли доктор", default=False, null=True)
    GotPills = models.CharField(
        choices=GotPills_choices, max_length=11, verbose_name="Получили ли вы лекарственые средства", null=True)

    def __str__(self):
        plus = ''
        symptoms = ['high_temperature', 'runny_nose', 'no_smell', 'weakness',
                    'muscle_pain', 'nausea', 'cough', 'dyspnea', 'diarrhea', 'vomiting']
        for i in symptoms:
            if getattr(self, i):
                plus = '+'
                break
        return f"{self.user.last_name} {self.date_time} {plus}"

    class Meta:
        verbose_name = "Результат опроса"
        verbose_name_plural = "Результаты опроса"
