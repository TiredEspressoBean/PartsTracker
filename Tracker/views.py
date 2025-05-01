import json
import uuid
from collections import OrderedDict

from django import forms
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.decorators import login_required
from django.forms import modelform_factory, modelformset_factory
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect, get_list_or_404, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.apps import apps
from formtools.wizard.views import SessionWizardView, NamedUrlSessionWizardView

from Tracker.generic_views import apply_styles_to_form
from Tracker.models import Parts, Deals, DealItems, PartTypes, Steps, User, Companies, Equipments, ErrorReports, \
    QualityErrorsList, Processes, PartDocs
from Tracker.forms import DealForm, PartTypeForm, ProcessForm, LineItemForm, LineItemFormSet, PartDocForm, PartsFormforDeals


# from Tracker.generic_views import apply_styles_to_form, apply_styles_to_formset

def tracker(request):
    context = {}
    user = request.user
    if user.is_authenticated:
        if user.is_staff:
            parts = get_list_or_404(Parts, archived=False)
            context.update({'parts': parts})
            deals = get_list_or_404(Deals, archived=False)
            context.update({'deals': deals})
        else:
            deals = Deals.objects.filter(customer=user)
            context.update({'deals': deals})
            parts = Parts.objects.filter(customer=user)
            context.update({'parts': parts})
    return render(request, template_name='tracker/tracker.html', context=context)


def upload(request):
    return None


@login_required
def part_view(request, part_id):
    context = {}
    part = get_object_or_404(Parts, id=part_id)
    customer = get_object_or_404(User, id=part.customer_id)
    company = get_object_or_404(Companies, id=part.deal.company.id)
    current_step = get_object_or_404(Steps, id=part.step_id)
    context.update({'part': part})
    context.update({'customer': customer})
    context.update({'company': company})
    context.update({'current_step': current_step})
    return render(request, 'tracker/part_view.html', context=context)


@login_required
def deal_view(request, deal_id):
    context = {}
    deal = get_object_or_404(Deals, id=deal_id)
    context.update({'deal': deal})

    return render(request, 'tracker/deal_view.html', context=context)


@staff_member_required
def edit(request):
    context = {}
    parts = get_list_or_404(Parts)
    for part in parts:
        deal = get_object_or_404(Deals, id=part.deal_id)
        part.customer = deal.customer
    deals = get_list_or_404(Deals)
    context.update({'parts': parts})
    context.update({'deals': deals})
    return render(request, 'tracker/edit.html', context=context)


@staff_member_required
def edit_deal(request, deal_id):
    deal = get_object_or_404(Deals, id=deal_id)
    deal_items = DealItems.objects.filter(deal=deal)
    customers = get_list_or_404(User, groups__name='Customers')
    companies = get_list_or_404(Companies)

    if request.method == "POST":
        # Update Deals Fields
        Deals.customer_id = request.POST.get("customer")
        Deals.estimated_completion = request.POST.get("estimated_delivery")
        Deals.save()

        # Update Deals Items
        updated_parts = request.POST.getlist("Deals_items")  # Get all selected parts

        # Remove any items that were not included in the form
        deal_items.exclude(part_id__in=updated_parts).delete()

        # Add new items if necessary
        existing_parts = deal_items.values_list("part_id", flat=True)
        for part_id in updated_parts:
            if int(part_id) not in existing_parts:
                part = get_object_or_404(Parts, id=part_id)
                DealItems.objects.create(Deals=Deals, part=part)

        messages.success(request, "Deals updated successfully!")
        return redirect("edit_Deals", Deals_id=deal.id)  # Redirect back after saving

    return render(
        request,
        "tracker/edit_deal.html",
        {"deal": deal, "deal_items": deal_items, "parts": Parts.objects.all(), "customers": customers,
         "companies": companies},
    )


@staff_member_required
def edit_part(request, part_id):
    part = get_object_or_404(Parts, id=part_id)

    if request.method == "POST":
        part.name = request.POST.get('name')
        part.part_type_id = request.POST.get('part_type')
        part.step_id = request.POST.get('step')
        part.is_complete = 'is_complete' in request.POST
        part.assigned_emp_id = request.POST.get('assigned_emp') or None
        part.customer_id = request.POST.get('customer')
        part.Deals_id = request.POST.get('Deals')
        part.estimated_completion = request.POST.get('estimated_completion') or None
        part.status = request.POST.get('status')
        part.save()
        return redirect('/edit_part/' + str(part.id))

    context = {
        'part': part,
        'part_types': PartTypes.objects.all(), 'steps': Steps.objects.filter(part_model_id=part.part_type.id),
        'employees': User.objects.filter(groups__name='Employees'),
        'customers': User.objects.filter(groups__name='Customers'),
        'Dealss': Deals.objects.all(),
        'status': Parts.Status.values,
    }
    return render(request, 'tracker/edit_part.html', context)


def home(request):
    return render(request, 'tracker/home.html', {"current_time": timezone.localtime()})


def create_page(request):
    return render(request, 'tracker/create_page.html')


class qa_page(View):
    def get(self, request):
        context = {}
        parts = get_list_or_404(Parts, archived=False)
        context["parts"] = parts
        return render(request, 'tracker/qa.html', context=context)

    def post(self, request, *args, **kwargs):
        part = get_object_or_404(Parts, id=request.POST.get('part_id'))
        if request.POST["action"] == "Pass":
            part_step = part.step
            if part_step.is_last_step == True:
                part.status = 'COMPLETED'
            else:
                next_step = get_object_or_404(Steps, part_model_id=part.part_type.id, step=(part_step.step + 1), process=part_step.process)
                part.step = next_step
                part.step_id = next_step.id
                part.save()
        elif request.POST["action"] == "Error":
            return redirect('error_form', part_id=part.id)
        elif request.POST["action"] == "Archive":
            part.archived = True
            part.save()
        return redirect('QA')


def docs(request):
    return None


def single_doc(request, doc_id):
    return None


def error_form(request, part_id):
    part = get_object_or_404(Parts, id=part_id)
    machines = Equipments.objects.all()
    employees = User.objects.filter(is_staff=1)
    error_types = QualityErrorsList.objects.filter(part_type=part.part_type)

    if request.method == "POST":
        machine_id = request.POST.get("machine")
        operator_name = request.POST.get("operator")
        description = request.POST.get("description")
        file = request.FILES.get("file")
        selected_errors = request.POST.getlist("errors")  # Get multiple selected errors
        other_error = request.POST.get("other_error", "").strip()  # Handle optional input

        if not selected_errors:
            messages.error(request, "At least one error type must be selected.")
        else:
            # Get Machine and Employee objects
            machine = Equipments.objects.filter(id=machine_id)
            operator = User.objects.filter(first_name__in=[operator_name.split()[0]], last_name__in=[
                operator_name.split()[-1]]).first() if operator_name else None

            # Save the error report manually
            error_report = ErrorReports.objects.create(
                part=part,
                machine=machine,
                operator=operator,
                description=description,
                file=file,
            )

            messages.success(request, "Error report submitted successfully.")
            return redirect("tracker:part_detail", part_id=part.id)  # Redirect after success

    context = {
        "part": part,
        "machines": machines,
        "employees": employees,
        "error_types": error_types,
    }

    return render(request, "tracker/error_form.html", context)

@staff_member_required()
def bulk_operations(request):
    context = {}
    deals = get_list_or_404(Deals, archived=False)
    context["deals"] = deals

    return render(request, 'tracker/bulk_operations.html', context=context)

@staff_member_required()
def bulk_edit_parts(request, deal_id):
    context = {}
    deal = get_object_or_404(Deals, id=deal_id)
    context["deal"] = deal
    return render(request, 'tracker/bulk_edit.html', context=context)


def bulk_processes(request):
    context = {}
    return render(request, "tracker/bulk_process.html", context=context)


def next_form_in_queue(request):
    queue = request.session.get('form_queue', [])

    if not queue:
        # All steps complete — redirect to final deal view
        deal_id = request.session.get('current_deal_id')
        return redirect('deal_view', deal_id=deal_id)

    next_form = queue.pop(0)
    request.session['form_queue'] = queue
    request.session['current_form_row'] = next_form['row']

    if next_form['type'] == 'part_type':
        return redirect('create/parttypes')
    elif next_form['type'] == 'process':
        return redirect('create/processes')

def archive_deal(request, deal_id):
    deal = get_object_or_404(Deals, id=deal_id)

    # Set deal as archived
    deal.archived = True
    deal.save()

    # Archive all related parts
    Parts.objects.filter(deal=deal).update(archived=True)

    return redirect('deal_view', deal_id=deal.id)


def add_lineitem_partial(request):
    form = LineItemForm(prefix=f"lineitem-{uuid.uuid4().hex[:6]}")
    html = render_to_string("tracker/partials/lineitem_row.html", {"form": form})
    return HttpResponse(html)

class DealCreateView(View):
    def get(self, request):
        deal_form = DealForm()
        lineitem_formset = LineItemFormSet(prefix="lineitem")
        return render(request, "tracker/deal_form.html", {
            "deal_form": deal_form,
            "lineitem_formset": lineitem_formset,
            "deal": None,
        })

    def post(self, request):
        deal_form = DealForm(request.POST)
        lineitem_formset = LineItemFormSet(request.POST, prefix="lineitem")

        if deal_form.is_valid() and lineitem_formset.is_valid():
            deal = deal_form.save()
            for form in lineitem_formset:
                item = form.save(commit=False)
                item.deal = deal
                item.save()
            return redirect("deal_view", deal_id=deal.id)

        return render(request, "tracker/deal_form.html", {
            "deal_form": deal_form,
            "lineitem_formset": lineitem_formset,
            "deal": None,
        })

class BulkCreateParts(View):
    def get(self, request):
        lineitem_formset = LineItemFormSet(prefix="lineitem")
        return render(request, "tracker/bulk_create_parts.html", {
            "lineitem_formset": lineitem_formset
        })                          

    def post(self, request):
        deal_form = DealForm(request.POST)
        lineitem_formset = LineItemFormSet(request.POST, prefix="lineitem")

        if deal_form.is_valid() and lineitem_formset.is_valid():
            deal = deal_form.save()
            for form in lineitem_formset:
                item = form.save(commit=False)
                item.deal = deal
                item.save()
            return redirect("deal_view", deal_id=deal.id)

        return render(request, "tracker/deal_form.html", {
            "deal_form": deal_form,
            "lineitem_formset": lineitem_formset,
            "deal": None,
        })

class DealUpdateView(View):
    def get(self, request, pk):
        deal = get_object_or_404(Deals, pk=pk)
        deal_form = DealForm(instance=deal)
        lineitem_formset = LineItemFormSet(prefix="lineitem", queryset=deal.dealitems_set.all())
        return render(request, "tracker/deal_form.html", {
            "deal_form": deal_form,
            "lineitem_formset": lineitem_formset,
            "deal": deal,
        })

    def post(self, request, pk):
        deal = get_object_or_404(Deals, pk=pk)
        deal_form = DealForm(request.POST, instance=deal)
        lineitem_formset = LineItemFormSet(request.POST, prefix="lineitem", queryset=deal.dealitems_set.all())

        if deal_form.is_valid() and lineitem_formset.is_valid():
            deal = deal_form.save()
            return redirect("deal_view", deal_id=deal.id)

        return render(request, "tracker/deal_form.html", {
            "deal_form": deal_form,
            "lineitem_formset": lineitem_formset,
            "deal": deal,
        })


def add_parttype_partial(request):
    if request.method == "GET":
        # Regular GET -> render a blank form (to add a new one dynamically)
        form = PartTypeForm(prefix=f"parttype-{uuid.uuid4().hex[:6]}")
        return render(request, "tracker/partials/parttype_row.html", {"form": form})

    elif request.method == "POST":
        form = PartTypeForm(request.POST, prefix=request.POST.get("prefix"))

        if form.is_valid():
            parttype = form.save()

            if request.headers.get('Hx-Request'):
                new_form = PartTypeForm(prefix=f"parttype-{uuid.uuid4().hex[:6]}")
                response = render(request, "tracker/partials/parttype_row.html", {"form": new_form})
                response["HX-Trigger"] = "refresh-lineitems"
                return response
            else:
                # Regular POST fallback
                return redirect("deal_form")

        else:
            # Form invalid: return the form with errors
            return render(request, "tracker/partials/parttype_row.html", {"form": form})


def add_process_partial(request):
    if request.method == "GET":
        form = ProcessForm(prefix=f"process-{uuid.uuid4().hex[:6]}")  # <-- fixed the wrong prefix
        return render(request, "tracker/partials/process_row.html", {"form": form})

    elif request.method == "POST":
        form = ProcessForm(request.POST, prefix=request.POST.get("prefix"))

        if form.is_valid():
            process = form.save()

            if request.headers.get('Hx-Request'):
                new_form = ProcessForm(prefix=f"process-{uuid.uuid4().hex[:6]}")
                response = render(request, "tracker/partials/process_row.html", {"form": new_form})
                response["HX-Trigger"] = "refresh-lineitems"
                return response
            else:
                return redirect("deal_form")

        else:
            return render(request, "tracker/partials/process_row.html", {"form": form})


def parttype_select_partial(request):
    part_types = PartTypes.objects.all()
    return render(request, "tracker/partials/parttype_select_options.html", {"part_types": part_types})


def process_select_partial(request):
    processes = Processes.objects.all()
    return render(request, "tracker/partials/process_select_options.html", {"processes": processes})

def refresh_parttype_process_selects(request):
    lineitem_formset = LineItemFormSet(prefix="lineitem")
    return render(request, "tracker/partials/lineitem_table.html", {
        "lineitem_formset": lineitem_formset,
    })

def upload_part_doc(request):
    if request.method == 'POST':
        form = PartDocForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.uploaded_by = request.user
            doc.save()
            return redirect('list_part_docs')
    else:
        form = PartDocForm()

    return render(request, 'tracker/part_doc_upload.html', {'form': form})


def list_part_docs(request):
    docs = PartDocs.objects.all()

    # Optional filter by part
    part_id = request.GET.get('part')
    if part_id:
        docs = docs.filter(part_id=part_id)

    return render(request, 'tracker/part_doc_list.html', {'docs': docs})


def generated_parts_for_deals_or_create(request):
    context = {}
    parts = []  # Initialize the list to store parts forms

    uuid_idxs = []

    for key in request.POST.keys():
        if key.startswith('lineitem-') and key.endswith('-quantity'):
            uuid_idxs.append(key.split('-')[1])

    for idx in uuid_idxs:  # Loop through line items in POST data
        # Get the quantity for the current line item
        if not request.POST[f'lineitem-{idx}-quantity'] or not request.POST[f'lineitem-{idx}-enumeration_start'] or not request.POST[f'lineitem-{idx}-part_type'] or not request.POST[f'lineitem-{idx}-process']:
            continue

        quantity = request.POST[f'lineitem-{idx}-quantity']

        for i in range(int(quantity)):  # For each quantity, create a form
            try:
                step = Steps.objects.get(step=1, process=request.POST[f'lineitem-{idx}-process'])
            except Steps.DoesNotExist:
                step = None  # Handle case where Step does not exist

            part_type = request.POST[f'lineitem-{idx}-part_type']
            glovia_id = PartTypes.objects.get(pk=part_type).ID_prefix

            if glovia_id:
                glovia_id += str(i + int(request.POST[f'lineitem-{idx}-enumeration_start']))
            else:
                glovia_id = 'No glovia id in database for this part type ' + str(i + int(request.POST[f'lineitem-{idx}-enumeration_start']))

            # Append the PartForm with the required initial data
            parts.append({
                'name':glovia_id,
                'form': PartsFormforDeals(initial={
                'part_type': part_type,
                'step': step,
                'glovia_id': glovia_id,
            })})

    # Pass the parts to the context
    context['parts'] = parts

    # Render the response with the updated context
    return render(request, 'tracker/partials/enumerated_parts_partial.html', context)
