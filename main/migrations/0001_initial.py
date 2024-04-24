# Generated by Django 4.0 on 2022-02-13 01:46

import datetime
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('patronymic', models.CharField(max_length=60, null=True, verbose_name='Отчество')),
                ('hospital', models.CharField(max_length=350, null=True, verbose_name='Больница')),
                ('section', models.CharField(max_length=200, null=True, verbose_name='Участок')),
                ('phone', models.CharField(max_length=12, null=True, verbose_name='Контактный номер')),
                ('iin', models.CharField(max_length=12, null=True, verbose_name='ИИН')),
                ('sex', models.CharField(choices=[('М', 'М'), ('Ж', 'Ж')], help_text='Выберите пол', max_length=7, null=True, verbose_name='Пол')),
                ('pcr', models.DateField(blank=True, null=True, verbose_name='Дата ПЦР')),
                ('isVaccianted', models.BooleanField(null=True, verbose_name='Наличие вакцины')),
                ('age', models.PositiveSmallIntegerField(null=True, verbose_name='Возраст')),
                ('status', models.CharField(choices=[('Пенсионер', 'Пенсионер'), ('Самозанятый', 'Самозанятый'), ('Работаю', 'Работаю'), ('Другое', 'Другое'), ('Учащийся', 'Учащийся'), ('Безработный', 'Безработный')], max_length=17, null=True, verbose_name='Занятость')),
                ('period', models.PositiveSmallIntegerField(default=0, verbose_name='Кол-во опросов')),
                ('days', models.PositiveSmallIntegerField(default=10, verbose_name='Лимит опросов')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'Пользователь',
                'verbose_name_plural': 'Пользователи',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('date_time', models.DateTimeField(default=datetime.datetime(2022, 2, 13, 1, 46, 15, 886890), verbose_name='Дата и время опроса')),
                ('high_temperature', models.BooleanField(default=False, null=True, verbose_name='Температура выше 37.0')),
                ('runny_nose', models.BooleanField(default=False, null=True, verbose_name='Насморк')),
                ('no_smell', models.BooleanField(default=False, null=True, verbose_name='Нет запахов')),
                ('weakness', models.BooleanField(default=False, null=True, verbose_name='Слабость')),
                ('muscle_pain', models.BooleanField(default=False, verbose_name='Боль в мышцах')),
                ('nausea', models.BooleanField(default=False, verbose_name='Тошнота')),
                ('cough', models.BooleanField(default=False, verbose_name='Кашель')),
                ('dyspnea', models.BooleanField(default=False, verbose_name='Одышка')),
                ('diarrhea', models.BooleanField(default=False, verbose_name='Диарея')),
                ('vomiting', models.BooleanField(default=False, verbose_name='Рвота')),
                ('isCalled', models.BooleanField(default=False, verbose_name='Звонил ли доктор')),
                ('GotPills', models.CharField(choices=[('Да', 'Да'), ('Нет', 'Нет'), ('Не нуждаюсь', 'Не нуждаюсь')], max_length=11, null=True, verbose_name='Получили ли вы лекарственые средства')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.customuser', verbose_name='Опрашиваемый')),
            ],
            options={
                'verbose_name': 'Результат опроса',
                'verbose_name_plural': 'Результаты опроса',
            },
        ),
    ]
