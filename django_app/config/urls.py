"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from pedidos import views
from pedidos.forms import CustomAuthenticationForm

class LogoutPostOnlyView(auth_views.LogoutView):
    http_method_names = ['post']
    next_page = 'login'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/',  auth_views.LoginView.as_view(
        template_name='pedidos/login.html',
        authentication_form=CustomAuthenticationForm
    ), name='login'),
    path('logout/', LogoutPostOnlyView.as_view(), name='logout'),
    path('registro/', views.RegistroView.as_view(), name='registro'),
    path('', include('pedidos.urls')),
]

handler403 = 'pedidos.views.handler_403'
