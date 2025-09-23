from django.urls import path
from . import views

app_name = 'website'

urlpatterns = [
    # Main pages
    path('', views.HomeView.as_view(), name='home'),
    path('services/', views.ServicesView.as_view(), name='services'),
    path('services/<slug:slug>/', views.ServiceDetailView.as_view(), name='service_detail'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('demos/', views.DemosView.as_view(), name='demos'),
    path('demos/<slug:slug>/', views.DemoDetailView.as_view(), name='demo_detail'),
    path('contact/', views.ContactView.as_view(), name='contact'),
]