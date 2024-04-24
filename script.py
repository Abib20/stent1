from datetime import timedelta
from main.models import Report, CustomUser
from django.db.models import F
from django.utils.timezone import now


def add_empty_report():
    users = CustomUser.objects.filter(is_staff=False, period__lt=F('days'))
    for user in users:
        yesterday = now() - timedelta(days=1)
        count_yesterdays_reports = Report.objects.filter(
            user=user, date_time__date=yesterday.date()).count()
        if count_yesterdays_reports == 0:
            Report.objects.create(
                user=user, date_time=yesterday, high_temperature=None, runny_nose=None, no_smell=None, weakness=None, muscle_pain=None, nausea=None, cough=None, dyspnea=None, diarrhea=None, vomiting=None, isCalled=None, GotPills=None)
    print(f'{users.count()} user(s) dont create report yesterday, so i created empty report for them!')
