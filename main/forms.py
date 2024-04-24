from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    age = forms.IntegerField(max_value=150, min_value=0, label='Возраст')
    phone = forms.CharField(widget=forms.TextInput(attrs={'pattern':'[0-9]*',
    'placeholder': '88005553535'}),
                            label='Контактный номер', max_length=12)
    iin = forms.CharField(widget=forms.TextInput(
        attrs={'pattern': '[0-9]{12}', 'placeholder': '12-ти значный код'}), label='ИИН')
    pcr = forms.DateField(widget=forms.SelectDateWidget(
        empty_label=("Год", "Месяц", "День")
    ), label='Дата ПЦР')

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('last_name', 'first_name', 'patronymic', 'sex', 'age', 'hospital', 'section', 'phone',
                  'iin', 'pcr', 'isVaccianted',  'status', 'username') + UserCreationForm.Meta.fields


class CustomUserChangeForm(UserChangeForm):

    class Meta(UserChangeForm):
        model = CustomUser
        fields = ('username', 'password', 'first_name', 'last_name', 'patronymic', 'sex', 'age',
                  'hospital', 'section', 'phone', 'iin', 'pcr', 'isVaccianted',  'status', 'period', 'days')
