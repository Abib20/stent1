from cov.celery import app
from celery.beat import crontab
from django.db.models import Q
from datetime import timedelta
import datetime
from main.models import Report, CustomUser
from django.db.models import F
from io import BytesIO
import xlsxwriter


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        # писать -5 часов относительно ЕКБ, 00:05 для казахов
        crontab(minute=5, hour=18),
        add_empty_report,
    )


@app.task
def add_empty_report():
    # убираем пользователей с истёкшим сроком
    users = CustomUser.objects.filter(is_staff=False).filter(period__lt=F('days')).filter(
        Q(date_joined__date__lt=datetime.datetime.today().date() - timedelta(days=1)*F('days')))
    for user in users:
        user.period = user.days
        user.save()
    users = CustomUser.objects.filter(is_staff=False, period__lt=F('days'))
    for user in users:
        user.period = Report.objects.filter(user=user).count()
        user.save()
    users = CustomUser.objects.filter(is_staff=False, period__lt=F('days'))
    empty_reports_count = 0
    for user in users:
        yesterday = datetime.datetime.today().date() - timedelta(days=1)
        count_yesterdays_reports = Report.objects.filter(
            user=user, date_time__date=yesterday).count()
        if count_yesterdays_reports == 0:
            Report.objects.create(
                user=user, date_time=yesterday, high_temperature=None, runny_nose=None, no_smell=None, weakness=None, muscle_pain=None, nausea=None, cough=None, dyspnea=None, diarrhea=None, vomiting=None, isCalled=None, GotPills=None)
            user.period = Report.objects.filter(user=user).count()
            user.save()
            empty_reports_count += 1
    print(f"{empty_reports_count} user(s) didn't create report yesterday, so i created empty report for them!")


def make_excel(json):
    if type(json) == list:
        headers = json[0].keys()

        output = BytesIO()
        file = xlsxwriter.Workbook(
            output, {'in_memory': True, 'remove_timezone': True})

        file_list = file.add_worksheet()

        for num, header in enumerate(headers):
            file_list.write(0, num, header)

        row_number = 1
        for row in json:
            for col, header in enumerate(row.keys()):
                file_list.write(row, col, row[header])
            row += 1
        file.close()
        output.seek(0)
        filename = 'otchet.xlsx'
        # response = HttpResponse(
        #     output,
        #     content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        # )
        # response['Content-Disposition'] = 'attachment; filename=%s' % filename
