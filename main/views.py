from xml.dom.pulldom import default_bufsize
from django.http import response
from django.http.response import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.contrib import messages
from cov.settings import EMAIL_HOST_USER
from main.forms import CustomUserCreationForm
from main.models import CustomUser, Report
import json
import datetime
from django.db.models import Q, F
import xlsxwriter
from django.core.mail import send_mail
from io import BytesIO


SYMPTOMS = ('high_temperature', 'runny_nose', 'no_smell', 'weakness', 'muscle_pain',
            'nausea', 'cough', 'dyspnea', 'diarrhea', 'vomiting')
SIGN = {'last_name': 'Фамилия', 'first_name': 'Имя', 'patronymic': 'Отчество',
        'section': 'Участок', 'phone': 'Телефон', 'iin': 'ИИН', 'sex': 'Пол', 'pcr': 'Дата ПЦР', 'isVaccianted': 'Привитость',
        'age': 'Возраст', 'status': 'Занятость'}
ZNAKI = {True: '+', False: '-', None: ''}


def get_verbose_name(x):
    return Report._meta.get_field(x).verbose_name


def get_user_verbose_name(x):
    return CustomUser._meta.get_field(x).verbose_name


def main_page(request):
    return render(request, 'main/index.html')


def register(request):
    if request.method == 'POST':
        user_form = CustomUserCreationForm(request.POST)
        if user_form.is_valid():
            user = user_form.save()
            messages.success(
                request, f'Привет {user.first_name}! Учётная запись создана. Теперь ты можешь войти.')
            return redirect('login')
    else:
        user_form = CustomUserCreationForm()

    return render(
        request,
        'main/register.html',
        {
            'user_form': user_form
        }
    )


def report_page(request):
    if request.method == 'POST':
        data = dict(request.POST)
        data.pop('csrfmiddlewaretoken')
        for item in data.items():
            if (item[0] != 'GotPills') and (item[1][0] in ('Yes', 'No')):
                data[item[0]] = item[1][0] == 'Yes'
        data["user"] = request.user
        user = CustomUser.objects.get(id=data['user'].id)

        if not Report.objects.filter(user=data['user'], date_time__date=datetime.datetime.today().date()).count():
            if user.period < user.days:
                Report.objects.create(**data)
                isSick = False
                for i in data.items():
                    if i[1] == True and i[0] not in ('isCalled', 'GotPills'):
                        isSick = True
                user.period = Report.objects.filter(user=data['user']).count()
                user.save()
                if isSick:
                    subject = 'У опрашиваемого появились симптомы covid-19!'
                    message = f'Опрашиваемый: {user.last_name} {user.first_name} {user.patronymic} {user.phone}'
                    send_mail(subject,
                              message, EMAIL_HOST_USER, ['covid24kz@yandex.ru'], fail_silently=False)
                return redirect("/")
            return HttpResponse("У вас закончился период прохождения опросов!")
        return HttpResponse("Сегодня вы уже проходили опрос, данные за сегодняшний день уже были внесены!")
    else:
        return render(request, 'main/report.html')


def login_page(request):
    return render(request, 'main/login.html')


def report_data(request):
    if request.method == 'GET':
        start_day = datetime.date.today() - datetime.timedelta(9)
        dates = [start_day + datetime.timedelta(i) for i in range(10)]
        data = {}
        for day_date in dates:
            day = str(day_date)
            reports = Report.objects.filter(date_time__date=day)
            sick_report = reports.filter(Q(high_temperature=True) |
                                         Q(runny_nose=True) | Q(no_smell=True) | Q(weakness=True) |
                                         Q(muscle_pain=True) | Q(nausea=True) | Q(cough=True) |
                                         Q(dyspnea=True) | Q(diarrhea=True) |
                                         Q(vomiting=True)
                                         )
            data[day] = {}
            data[day]['sick_count'] = len(sick_report)
            if day_date == datetime.date.today():
                data['all_count'] = len(reports)
                data['sick_count'] = len(sick_report)
                for symptom in SYMPTOMS:
                    data[day][symptom] = len(
                        sick_report.filter(**{symptom: True}))
        return HttpResponse(json.dumps(data), content_type="application/json")
    else:
        return Http404(request)


def report_data1(request):
    if request.method == 'GET':
        if request.GET['Today'] != 'null':
            today = datetime.datetime.strptime(
                request.GET['Today'], '%Y-%m-%d').date()
            today = today if today == datetime.date.today() else datetime.date.today()
        else:
            today = datetime.date.today()
        start_day = today - datetime.timedelta(9)
        dates = [start_day + datetime.timedelta(i) for i in range(10)]
        data = {}
        for day_date in dates:
            sick_report = Report.objects.filter(
                user__is_staff=False, date_time__date=day_date)
            sick_report = sick_report.filter(Q(high_temperature=True) |
                                             Q(runny_nose=True) | Q(no_smell=True) | Q(weakness=True) |
                                             Q(muscle_pain=True) | Q(nausea=True) | Q(cough=True) |
                                             Q(dyspnea=True) | Q(diarrhea=True) |
                                             Q(vomiting=True)
                                             )
            data[str(day_date)] = sick_report.count()

        return HttpResponse(json.dumps(data, default=str), content_type="application/json")
    else:
        return Http404(request)


def report_symptoms_count(request):
    '''Получение числа пациентов, по каждому симтому за выбранную дату'''
    if request.method == 'GET':
        choosen_date = datetime.datetime.strptime(
            request.GET['date'], '%Y-%m-%d').date()
        symptoms_count = {}
        for name in SYMPTOMS:
            symptoms_count[name] = Report.objects.filter(
                date_time__date=choosen_date, user__is_staff=False, **{name: True}).count()
        return HttpResponse(json.dumps(symptoms_count), content_type="application/json")
    return Http404(request)


def report_ASH_count(request):
    '''Получение числа всех, только с наличием хотя бы одного симптома, без симптомов результатов опросов за выбранную дату'''
    if request.method == 'GET':
        choosen_date = datetime.datetime.strptime(
            request.GET['date'], '%Y-%m-%d').date()
        response = {}
        all_reports = Report.objects.filter(
            date_time__date=choosen_date, user__is_staff=False)
        response['all'] = all_reports.count()
        sick_reports = all_reports.filter(Q(high_temperature=True) |
                                          Q(runny_nose=True) | Q(no_smell=True) | Q(weakness=True) |
                                          Q(muscle_pain=True) | Q(nausea=True) | Q(cough=True) |
                                          Q(dyspnea=True) | Q(diarrhea=True) |
                                          Q(vomiting=True)
                                          )
        response['sick'] = sick_reports.count()
        response['health'] = all_reports.filter(
            **{symptom: False for symptom in SYMPTOMS}).count()
        return HttpResponse(json.dumps(response), content_type="application/json")
    return Http404(request)


def report_all(request):
    '''Получение всех опросов за выбранный день'''
    if request.method == 'GET':
        choosen_date = datetime.datetime.strptime(
            request.GET['date'], '%Y-%m-%d').date()
        all_reports = Report.objects.filter(
            date_time__date=choosen_date, user__is_staff=False).values('user', 'high_temperature', 'runny_nose', 'no_smell',
                                                                       'weakness', 'muscle_pain', 'nausea', 'cough', 'dyspnea', 'diarrhea', 'vomiting')
        all_reports = list(all_reports)
        res = []
        for report in all_reports:
            user = CustomUser.objects.get(id=report['user'])
            report = {get_verbose_name(item[0]): item[1]
                      for item in report.items()}
            for i in SIGN.items():
                report[i[1]] = getattr(user, i[0])
            report = {item[0]: (ZNAKI[item[1]] if type(
                item[1]) == bool else item[1]) for item in report.items()}
            report.pop('Опрашиваемый')
            res.append(report)

        return HttpResponse(json.dumps(res, default=str), content_type="application/json")
    else:
        return Http404(request)


def report_sick(request):
    '''Получение всех опросов с симптомами за выбранный день'''
    if request.method == 'GET':
        choosen_date = datetime.datetime.strptime(
            request.GET['date'], '%Y-%m-%d').date()
        sick_reports = Report.objects.filter(
            date_time__date=choosen_date, user__is_staff=False)
        sick_reports = sick_reports.filter(Q(high_temperature=True) |
                                           Q(runny_nose=True) | Q(no_smell=True) | Q(weakness=True) |
                                           Q(muscle_pain=True) | Q(nausea=True) | Q(cough=True) |
                                           Q(dyspnea=True) | Q(diarrhea=True) |
                                           Q(vomiting=True)
                                           )
        sick_reports = sick_reports.values('user', 'high_temperature', 'runny_nose', 'no_smell',
                                           'weakness', 'muscle_pain', 'nausea', 'cough', 'dyspnea', 'diarrhea', 'vomiting')
        sick_reports = list(sick_reports)
        res = []
        for report in sick_reports:
            user = CustomUser.objects.get(id=report['user'])
            report = {get_verbose_name(item[0]): item[1]
                      for item in report.items()}
            for i in SIGN.items():
                report[i[1]] = getattr(user, i[0])
            report = {item[0]: (ZNAKI[item[1]] if type(
                item[1]) == bool else item[1]) for item in report.items()}
            report.pop('Опрашиваемый')
            res.append(report)

        return HttpResponse(json.dumps(res, default=str), content_type="application/json")
    else:
        return Http404(request)


def report_health(request):
    '''Получение всех опросов без симптомов за выбранный день'''
    if request.method == 'GET':
        choosen_date = datetime.datetime.strptime(
            request.GET['date'], '%Y-%m-%d').date()
        health_reports = Report.objects.filter(
            date_time__date=choosen_date, user__is_staff=False)
        health_reports = health_reports.filter(
            **{symptom: False for symptom in SYMPTOMS})
        health_reports = health_reports.values('user', 'high_temperature', 'runny_nose', 'no_smell',
                                               'weakness', 'muscle_pain', 'nausea', 'cough', 'dyspnea', 'diarrhea', 'vomiting')
        health_reports = list(health_reports)
        res = []
        for report in health_reports:
            user = CustomUser.objects.get(id=report['user'])
            report = {get_verbose_name(item[0]): item[1]
                      for item in report.items()}
            for i in SIGN.items():
                report[i[1]] = getattr(user, i[0])
            report = {item[0]: (ZNAKI[item[1]] if type(
                item[1]) == bool else item[1]) for item in report.items()}
            report.pop('Опрашиваемый')
            res.append(report)

        return HttpResponse(json.dumps(res, default=str), content_type="application/json")
    else:
        return Http404(request)


def report_symptom(request):
    if request.method == 'POST':
        symptom = request.body.decode('UTF-8').strip('"')
        reports = list(Report.objects.filter(date_time__date=datetime.date.today(), ).filter(**{symptom: True}).values('user', 'high_temperature', 'runny_nose', 'no_smell', 'weakness', 'muscle_pain',
                                                                                                                       'nausea', 'cough', 'dyspnea', 'diarrhea', 'vomiting'))
        symptoms = {'user': 'Опрашиваемый', 'high_temperature': 'Высокая температура', 'runny_nose': 'Насморк', 'no_smell': 'Нет запахов', 'weakness': 'Слабость', 'muscle_pain': 'Боль в мышцах',
                    'nausea': 'Тошнота', 'cough': 'Кашель', 'dyspnea': 'Одышка',  'diarrhea': 'Диарея', 'vomiting': 'Рвота'}
        res = []
        for report in reports:
            user = CustomUser.objects.get(id=report['user'])
            report = {symptoms[item[0]]: item[1] for item in report.items()}
            for i in SIGN.items():
                report[i[1]] = getattr(user, i[0])
            report = {item[0]: (ZNAKI[item[1]] if (item[1] is True) or (
                item[1] is False) else item[1])for item in report.items()}
            report['Дата ПЦР'] = str(report['Дата ПЦР'])
            report.pop('Опрашиваемый')
            res.append(report)
        return HttpResponse(json.dumps(res), content_type="application/json")
    elif request.method == 'GET':
        symptom, choosen_date = request.GET.values()
        choosen_date = datetime.datetime.strptime(
            choosen_date, '%Y-%m-%d').date()
        reports = Report.objects.filter(
            user__is_staff=False, date_time__date=choosen_date).filter(**{symptom: True})
        reports = reports.values('user', 'high_temperature', 'runny_nose', 'no_smell',
                                 'weakness', 'muscle_pain', 'nausea', 'cough', 'dyspnea', 'diarrhea', 'vomiting')
        reports = list(reports)

        res = []
        for report in reports:
            user = CustomUser.objects.get(id=report['user'])
            report = {get_verbose_name(  # можно оптимизировать
                item[0]): item[1] for item in report.items()}
            for i in SIGN.items():
                report[i[1]] = getattr(user, i[0])
            report = {item[0]: (ZNAKI[item[1]] if type(
                item[1]) == bool else item[1]) for item in report.items()}
            report.pop('Опрашиваемый')
            res.append(report)
        return HttpResponse(json.dumps(res, default=str), content_type="application/json")
    else:
        return Http404(request)


def graphics(request):
    if request.method == "GET":
        return render(request, 'main/graphics.html')
    return Http404(request)


def test(request):
    if request.method == "GET":
        return render(request, 'main/test_graphics.html')
    return Http404(request)


def download_data(request):
    if request.method == "POST":
        data = json.loads(request.body)
        output = BytesIO()
        file = xlsxwriter.Workbook(
            output, {'in_memory': True, 'remove_timezone': True})

        file_list = file.add_worksheet()
        headers = ('ДАТА ПЦР', 'Дата заполнения опросника', 'ФИО', 'Пол', 'Возраст', 'Контактный номер', 'Занятость', 'ИИН', 'Наличие вакцинации', 'Наименование медицинской организации',
                   'Участок', 'Температура выше 37.5', 'Насморк', 'Нет запахов', 'Слабость', 'Боль в мышцах', 'Тошнота', 'Кашель', 'Одышка', 'Диарея', 'Рвота', 'Звонил ли доктор', 'Выданы ЛС')
        row = 0
        for num, header in enumerate(headers):
            file_list.write(row, num, header)
        users = CustomUser.objects.filter(is_staff=False)

        row += 1

        for user in users:
            user_stats = {
                '0': getattr(user, 'pcr', None),
                '2': ' '.join((getattr(user, 'last_name', ''), getattr(user, 'first_name', ''), getattr(user, 'patronymic', ''))),
                '3': getattr(user, 'sex', None),
                '4': getattr(user, 'age', None),
                '5': getattr(user, 'phone', None),
                '6': getattr(user, 'status', None),
                '7': getattr(user, 'iin', None),
                '8': getattr(user, 'isVaccianted', None),
                '9': getattr(user, 'hospital', None),
                '10': getattr(user, 'section', None),
            }
            user_stats['8'] = 'Да' if user_stats['8'] else 'Нет'
            user_stats['0'] = user_stats['0'].strftime("%d.%m.%Y")
            reports = Report.objects.filter(
                user=user, date_time__date__gte=datetime.datetime.strptime(data['start'], '%Y-%m-%d').date(), date_time__date__lte=datetime.datetime.strptime(data['end'], '%Y-%m-%d').date())
            for report in reports:
                reports_stats = {
                    '1': getattr(report, 'date_time', None),
                    '11': getattr(report, 'high_temperature', None),
                    '12': getattr(report, 'runny_nose', None),
                    '13': getattr(report, 'no_smell', None),
                    '14': getattr(report, 'weakness', None),
                    '15': getattr(report, 'muscle_pain', None),
                    '16': getattr(report, 'nausea', None),
                    '17': getattr(report, 'cough', None),
                    '18': getattr(report, 'dyspnea', None),
                    '19': getattr(report, 'diarrhea', None),
                    '20': getattr(report, 'vomiting', None),
                    '21': getattr(report, 'isCalled', None),
                }
                for num, val in reports_stats.items():
                    if type(val) == bool:
                        if val:
                            reports_stats[num] = 'Есть'
                        else:
                            reports_stats[num] = 'Нет'
                reports_stats['1'] = reports_stats['1'].strftime(
                    "%d.%m.%Y %H:%M:%S")
                for col, val in user_stats.items():
                    file_list.write(row, int(col), val)
                for col, val in reports_stats.items():
                    file_list.write(row, int(col), val)
                row += 1
        file.close()
        output.seek(0)
        filename = 'otchet.xlsx'
        response = HttpResponse(
            output,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=%s' % filename

        return response
    return Http404(request)


def get_without_reports(request):
    '''Получение пациентов, которым не прошли опрос в выбранную дату'''
    if request.method == 'GET':
        choosen_date = datetime.datetime.strptime(
            request.GET['date'], '%Y-%m-%d').date()
        response = []
        # Можно оптимизировать
        if choosen_date == datetime.datetime.today().date():
            # получаем список юзеров кто прошёл опрос
            users_with_reports = list(Report.objects.filter(
                date_time__date=choosen_date, user__is_staff=False).values('user'))
            users_with_reports = set([user['user']
                                     for user in users_with_reports])
            all_users = list(CustomUser.objects.filter(
                is_staff=False, period__lt=F('days')).values('id'))
            all_users = set([user['id'] for user in all_users])
            users_without_reports = all_users.difference(users_with_reports)
            for user_id in users_without_reports:
                user = CustomUser.objects.values(*SIGN.keys()).get(id=user_id)
                c_user = {}
                for i in SIGN.items():
                    c_user[i[1]] = user[i[0]]
                c_user['Привитость'] = ZNAKI[c_user['Привитость']]
                response.append(c_user)
        else:
            reports = Report.objects.filter(date_time__date=choosen_date).filter(
                user__is_staff=False).filter(**{symptom: None for symptom in SYMPTOMS}).values('user')
            for report in list(reports):
                user = CustomUser.objects.values(
                    *SIGN.keys()).get(id=report['user'])
                c_user = {}
                for i in SIGN.items():
                    c_user[i[1]] = user[i[0]]
                c_user['Привитость'] = ZNAKI[c_user['Привитость']]
                response.append(c_user)
        return HttpResponse(json.dumps(response, default=str), content_type="application/json")
    return Http404(request)


def get_uncalled_reports(request):
    '''Получение пациентов, которым не звонили в выбранную дату'''
    if request.method == 'GET':
        choosen_date = datetime.datetime.strptime(
            request.GET['date'], '%Y-%m-%d').date()
        response = []
        reports = Report.objects.filter(date_time__date=choosen_date).filter(
            user__is_staff=False).filter(isCalled=False).values(*list(SYMPTOMS), 'user')
        for report in reports:
            user = CustomUser.objects.values(*SIGN.keys()).get(
                id=report['user'])
            c_user = {}
            for i in SIGN.items():
                c_user[i[1]] = user[i[0]]
            c_user['Привитость'] = ZNAKI[c_user['Привитость']]
            response.append(c_user)
        return HttpResponse(json.dumps(response, default=str), content_type="application/json")
    return Http404(request)


def get_reports_with_triple_symptoms(request):
    '''Получение пациентов и их отчётов в которых 3 и более симптома'''
    if request.method == 'GET':
        choosen_date = datetime.datetime.strptime(
            request.GET['date'], '%Y-%m-%d').date()
        response = []
        reports = Report.objects.filter(date_time__date=choosen_date).filter(
            user__is_staff=False).values(*list(SYMPTOMS), 'user')
        for report in list(reports):
            if list(report.values()).count(True) >= 3:
                user = CustomUser.objects.get(id=report['user'])
                report = {get_verbose_name(  # можно оптимизировать
                    item[0]): item[1] for item in report.items()}
                for i in SIGN.items():  # отказавшись от getattr
                    report[i[1]] = getattr(user, i[0])
                report = {item[0]: (ZNAKI[item[1]] if type(
                    item[1]) == bool else item[1]) for item in report.items()}
                report.pop('Опрашиваемый')
                response.append(report)
        return HttpResponse(json.dumps(response, default=str), content_type="application/json")
    return Http404(request)


def get_reports_with_triple_symptoms_three_days(request):
    '''Получение пациентов и их отчётов в которых 3 симптома 3 дня подряд'''
    if request.method == 'GET':
        choosen_date = datetime.datetime.strptime(
            request.GET['date'], '%Y-%m-%d').date()

        users1 = set()
        reports1 = list(Report.objects.filter(date_time__date=choosen_date).filter(
            user__is_staff=False).values(*list(SYMPTOMS), 'user'))
        for report in reports1:
            if list(report.values()).count(True) >= 3:
                users1.add(report['user'])

        users2 = set()
        reports2 = list(Report.objects.filter(date_time__date=choosen_date-datetime.timedelta(1)).filter(
            user__is_staff=False).values(*list(SYMPTOMS), 'user'))
        for report in reports2:
            if report['user'] in users1:
                if list(report.values()).count(True) >= 3:
                    users2.add(report['user'])

        users3 = set()
        reports3 = list(Report.objects.filter(date_time__date=choosen_date-datetime.timedelta(2)).filter(
            user__is_staff=False).values(*list(SYMPTOMS), 'user'))
        for report in reports3:
            if list(report.values()).count(True) >= 3:
                users3.add(report['user'])

        # юзеры у которых 3 дня подряд 3 и более симптомов,
        # но не обязательно одни и те же симтомы
        users = users1.intersection(users2, users3)
        end_users = set()
        for user in users:
            reports = list(Report.objects.filter(user__is_staff=False, user=user).filter(
                date_time__date__lte=choosen_date).filter(date_time__date__gte=choosen_date-datetime.timedelta(3)).values(*list(SYMPTOMS)))
            reports1 = set(
                [key for key, value in reports[0].items() if value])
            reports2 = set(
                [key for key, value in reports[1].items() if value])
            reports3 = set(
                [key for key, value in reports[2].items() if value])
            if len(reports1.intersection(reports2, reports3)) >= 3:
                end_users.add(user)

        # end_users сейчас хранит юзеров которые полностью удовлетворяют условию
        response = []
        for user in end_users:
            reports = list(Report.objects.filter(user__is_staff=False, user=user).filter(
                date_time__date__lte=choosen_date).filter(date_time__date__gte=choosen_date-datetime.timedelta(3)).values(*list(SYMPTOMS)))
            user = CustomUser.objects.filter(id=user).values(*SIGN.keys())
            for i in SIGN.items():
                user[i[1]] = getattr(user, i[0])
            row = {}
            for symptom in SYMPTOMS:
                row[symptom] = '-'
                counter = 0
                for report in reports:
                    if report[symptom]:
                        counter += 1
                        row[symptom] = f'+({counter})'
            row = {get_verbose_name(item[0]): item[1]
                   for item in row.items()}
            user.update(row)
            response.append(user)

        return HttpResponse(json.dumps(response, default=str), content_type="application/json")
    return Http404(request)


def get_reports_with_symptom_three_days(request):
    '''Получение пациентов и их отчётов в которых симптом 3 дня подряд'''
    if request.method == 'GET':
        choosen_date = datetime.datetime.strptime(
            request.GET['date'], '%Y-%m-%d').date()
        reports_three_days = Report.objects.filter(
            date_time__date__lte=choosen_date).filter(date_time__date__gte=choosen_date - datetime.timedelta(2)).filter(user__is_staff=False).filter(Q(high_temperature=True) | Q(runny_nose=True) | Q(no_smell=True)
                                                                                                                                                     | Q(weakness=True) | Q(muscle_pain=True) | Q(nausea=True)
                                                                                                                                                     | Q(cough=True) | Q(dyspnea=True) | Q(diarrhea=True) | Q(vomiting=True))
        all_users = reports_three_days.values('user')
        users = []
        for user in all_users:
            reports = reports_three_days.filter(
                user__id=user['user']).values(*list(SYMPTOMS))
            if reports.count() == 3:
                symptoms = []
                for report in reports:
                    symptoms.append({key: report[key] for key in SYMPTOMS})
                for key in SYMPTOMS:
                    if reports[0][key] == reports[1][key] == reports[2][key]:
                        users.append(user)
                        break
        users = [dict(t) for t in {tuple(d.items()) for d in users}]
        response = []
        for user_id in users:
            reports = list(Report.objects.filter(user__is_staff=False, user=user_id['user']).filter(
                date_time__date__lte=choosen_date).filter(date_time__date__gte=choosen_date-datetime.timedelta(2)).values(*list(SYMPTOMS)))
            с_user = CustomUser.objects.values(
                *SIGN.keys()).get(id=user_id['user'])
            user = {}
            for i in SIGN.items():
                user[i[1]] = с_user[i[0]]
            row = {}
            for symptom in SYMPTOMS:
                row[symptom] = '-'
                counter = 0
                for report in reports:
                    if report[symptom]:
                        counter += 1
                        row[symptom] = f'+({counter})'
            row = {get_verbose_name(item[0]): item[1]
                   for item in row.items()}
            user.update(row)
            response.append(user)
        return HttpResponse(json.dumps(response, default=str), content_type="application/json")
    return Http404(request)


def download_excel_file(request):
    if request.method == "POST":
        data = json.loads(request.body)
        headers = data[0].keys()
        output = BytesIO()
        file = xlsxwriter.Workbook(
            output, {'in_memory': True, 'remove_timezone': True})
        file_list = file.add_worksheet()
        for num, header in enumerate(headers):
            file_list.write(0, num, header)
        row_number = 1
        for row in data:
            for col, header in enumerate(row.keys()):
                file_list.write(row_number, col, row[header])
            row_number += 1
        file.close()
        output.seek(0)
        filename = 'otchet.xlsx'
        response = HttpResponse(
            output,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
    return Http404(request)
