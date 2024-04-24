from django.contrib import admin
from django.urls import path, include
from main.admin import admin_site
from main import views
from django.views.generic import TemplateView
urlpatterns = [
    path('admin/download/download_data/', views.download_data),
    path('admin/download/',
         TemplateView.as_view(template_name='admin/filter_export.html')),
    path('admin/', admin_site.urls),
    path('default_admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('main.urls'))
]
