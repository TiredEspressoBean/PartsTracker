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
from Tracker.forms import DealForm
from Tracker.generic_views import GenericCreateEntry, GenericUpdateEntry, GenericDeleteEntry, GenericViewEntry
from Tracker.views import DealUpdateView, DealCreateView

urlpatterns = [

    path("__reload__/", include("django_browser_reload.urls")),

    path("accounts/", include("django.contrib.auth.urls")),
    path('admin/', admin.site.urls, name='admin'),
    path('', views.home, name='home'),
    path('tracker/', views.tracker, name='tracker'),
    path('part_view/<int:part_id>/', views.part_view, name='part_view'),
    path('deal_view/<int:deal_id>/', views.deal_view, name='deal_view'),
    path('edit_part/<int:part_id>/', views.edit_part, name='edit_part'),
    path('edit_deal/<int:deal_id>/', views.edit_deal, name='edit_deal'),
    path('edit/', views.edit, name='edit'),
    path('upload/', views.upload),
    path('docs', views.docs, name='docs'),
    path('docs/<int:doc_id>', views.single_doc, name='docs'),

    path("accounts/", include("allauth.urls")),

    path("create/", views.create_page, name='create_page'),

    path("create/<str:model_name>", GenericCreateEntry.as_view(), name="create_page"),

    path("update/<str:model_name>/<int:pk>", GenericUpdateEntry.as_view(), name="update_entry"),

    path("delete/<str:model_name>/<int:pk>", GenericDeleteEntry.as_view(), name="delete_entry"),

    path("view/<str:model_name>/<int:pk>", GenericViewEntry.as_view(), name="view_entry"),

    path("QA", views.qa_page.as_view(), name="QA"),

    path("error_form/<int:part_id>", views.error_form, name="error_form"),

    path("bulk_operations", views.bulk_operations, name="bulk_operations"),

    path("bulk_edit/<int:deal_id>", views.bulk_edit_parts, name="bulk_edit"),

    path("bulk_processes", views.bulk_processes, name="bulk_processes"),

    path('deals/<int:deal_id>/archive/', views.archive_deal, name='archive_deal'),

]
# TODO: Add docs paths: Docs - for all docs, Doc/part_id for docs related to that part

urlpatterns += staticfiles_urlpatterns()

urlpatterns += [
    path("deals/lineitem/new/", views.add_lineitem_partial, name="add_lineitem_partial"),

    path('bulk_create_parts/', views.BulkCreateParts.as_view(), name='bulk_create_parts'),

    path('generated_parts', views.generated_parts_for_deals_or_create, name="generated_parts_for_deals_or_create"),
]

urlpatterns += [
    path("deals/new/", DealCreateView.as_view(), name="deal_create"),
    path("deals/<int:pk>/edit/", DealUpdateView.as_view(), name="deal_edit"),

    path("partials/parttype_row/", views.add_parttype_partial, name="add_parttype_partial"),
    path("partials/process_row/", views.add_process_partial, name="add_process_partial"),

    path('partials/parttype_select/', views.parttype_select_partial, name='parttype_select_partial'),

    path('partials/process_select/', views.process_select_partial, name='process_select_partial'),

    path("partials/refresh-lineitems/", views.refresh_parttype_process_selects, name="refresh_parttype_process_selects"),


]

urlpatterns += [
    path('docs/', views.list_part_docs, name='list_part_docs'),
    path('docs/upload/', views.upload_part_doc, name='upload_part_doc'),
]