"""
URL configuration for PizzaTrackerAmbac project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path
from django.urls.conf import include

from Tracker import views

urlpatterns = [
    path("accounts/", include("django.contrib.auth.urls")),
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('tracker/', views.tracker, name='tracker'),
    path('part_view/<int:part_id>/', views.part_view, name='part_view'),
    path('order_view/<int:order_id>/', views.order_view, name='order_view'),
    path('edit_part/<int:part_id>/', views.edit_part, name='edit_part'),
    path('edit_order/<int:order_id>/', views.edit_order, name='edit_order'),
    path('edit/', views.edit, name='edit'),
    path('upload/', views.upload),
    path('docs/<int:doc_id>', views.docs, name='docs'),
    path("accounts/", include("allauth.urls")),
]
# TODO: Add docs paths: Docs - for all docs, Doc/part_id for docs related to that part

urlpatterns += staticfiles_urlpatterns()