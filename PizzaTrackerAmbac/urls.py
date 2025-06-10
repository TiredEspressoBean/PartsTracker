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
from Tracker.hubspot_view import hubspot_webhook
from Tracker.views import OrderUpdateView, OrderCreateView, ErrorFormView

from Tracker.AI_view import chat_ai_view
urlpatterns = [

    path("__reload__/", include("django_browser_reload.urls")),

    path("accounts/", include("django.contrib.auth.urls")),

    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('admin/', admin.site.urls, name='admin'),
    path('', views.home, name='home'),
    path('tracker/', views.tracker, name='tracker'),
    path('part_view/<int:part_id>/', views.part_view, name='part_view'),
    path('deal_view/<int:order_id>/', views.deal_view, name='deal_view'),

    # TODO: Think I got rid of all uses of these two but not sure?
    path('edit_part/<int:part_id>/', views.edit_part, name='edit_part'),
    path('edit_deal/<int:deal_id>/', views.edit_deal, name='edit_deal'),
    path('edit/', views.edit, name='edit'),

    path("accounts/", include("allauth.urls")),

    path("create/<str:model_name>", GenericCreateEntry.as_view(), name="create_page"),

    path("update/<str:model_name>/<int:pk>", GenericUpdateEntry.as_view(), name="update_entry"),

    path("delete/<str:model_name>/<int:pk>", GenericDeleteEntry, name="delete_entry"),

    path("view/<str:model_name>/<int:pk>", GenericViewEntry.as_view(), name="view_entry"),

    path("QA", views.qa_page.as_view(), name="QA"),

    path("error_form/<int:part_id>", ErrorFormView.as_view(), name="error_form"),

    path("qa_orders", views.qa_orders, name="qa_orders"),

    path("bulk_edit/<int:order_id>", views.bulk_edit_parts, name="bulk_edit"),

    path('deals/<int:order_id>/archive/', views.archive_deal, name='archive_deal'),


]

urlpatterns += staticfiles_urlpatterns()

urlpatterns += [
    path("deals/lineitem/new/", views.add_lineitem_partial, name="add_lineitem_partial"),

    path('bulk_create_parts/', views.BulkCreateParts.as_view(), name='bulk_create_parts'),

    path("orders/<int:order_id>/export-parts/", views.export_parts_csv, name="export_parts_csv"),

    path("orders/<int:order_id>/upload-parts/", views.upload_parts_csv, name="upload_parts_csv"),
]

urlpatterns += [
    path("deals/new/", OrderCreateView.as_view(), name="deal_create"),
    path("deals/<int:order_id>/edit/", OrderUpdateView.as_view(), name="deal_edit"),

    path("deal_pass/<int:order_id>/", views.deal_pass, name="deal_pass"),

    path("partials/parttype_row/", views.add_parttype_partial, name="add_parttype_partial"),
    path("partials/process_row/", views.add_process_partial, name="add_process_partial"),

    path('partials/parttype_select/', views.parttype_select_partial, name='parttype_select_partial'),

    path('partials/process_select/', views.process_select_partial, name='process_select_partial'),

    path("partials/refresh-lineitems/", views.refresh_parttype_process_selects, name="refresh_parttype_process_selects"),

    path("tables/generic_table_view/<str:model_name>", views.generic_table_view, name="generic_table_view"),

    path("edit_model_page/<str:model_name>", views.edit_model_page, name="edit_model_page"),
]

urlpatterns += [
    path("part_docs", views.list_part_docs, name="list_part_docs"),
    path("download/<str:model_name>/<int:pk>/<str:field>/", views.download_file, name="download_file"),

    path("upload_part_doc", views.upload_part_doc, name="upload_part_doc"),
]

urlpatterns += [
    path("chat/", chat_ai_view.as_view(), name="chat_ai_view"),

    path("webhooks/hubspot/", hubspot_webhook, name="hubspot_webhook"),
]