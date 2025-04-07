from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.decorators import login_required
from django.forms import modelform_factory
from django.http import Http404
from django.shortcuts import render, redirect, get_list_or_404, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.apps import apps

from Tracker.models import Part, Deal, DealItem, PartType, Step, User, Companies, Equipment, ErrorReport, \
    QualityErrorsList


# Create your views here.


def tracker(request):
    context = {}
    user = request.user
    if user.is_authenticated:
        if user.is_staff:
            parts = get_list_or_404(Part)
            context.update({'parts': parts})
            deals = get_list_or_404(Deal)
            context.update({'deals': deals})
        else:
            deals = get_list_or_404(Deal, customer=user)
            context.update({'Deals': deals})
            parts = get_list_or_404(Part, customer=user)
            context.update({'parts': parts})
    return render(request, template_name='tracker/tracker.html', context=context)


def upload(request):
    return None


@login_required
def part_view(request, part_id):
    context = {}
    part = get_object_or_404(Part, id=part_id)
    customer = get_object_or_404(User, id=part.customer_id)
    company = get_object_or_404(Companies, id=part.deal.company.id)
    current_step = get_object_or_404(Step, id=part.step_id)
    context.update({'part': part})
    context.update({'customer': customer})
    context.update({'company': company})
    context.update({'current_step': current_step})
    return render(request, 'tracker/part_view.html', context=context)


@login_required
def deal_view(request, deal_id):
    context = {}
    deal = get_object_or_404(Deal, id=deal_id)
    context.update({'deal': deal})

    return render(request, 'tracker/deal_view.html', context=context)


@staff_member_required
def edit(request):
    context = {}
    parts = get_list_or_404(Part)
    for part in parts:
        deal = get_object_or_404(Deal, id=part.deal_id)
        part.customer = deal.customer
    deals = get_list_or_404(Deal)
    context.update({'parts': parts})
    context.update({'deals': deals})
    return render(request, 'tracker/edit.html', context=context)


@staff_member_required
def edit_deal(request, deal_id):
    deal = get_object_or_404(Deal, id=deal_id)
    deal_items = DealItem.objects.filter(deal=deal)
    customers = get_list_or_404(User, groups__name='Customers')
    companies = get_list_or_404(Companies)

    if request.method == "POST":
        # Update Deal Fields
        Deal.customer_id = request.POST.get("customer")
        Deal.estimated_completion = request.POST.get("estimated_delivery")
        Deal.save()

        # Update Deal Items
        updated_parts = request.POST.getlist("Deal_items")  # Get all selected parts

        # Remove any items that were not included in the form
        deal_items.exclude(part_id__in=updated_parts).delete()

        # Add new items if necessary
        existing_parts = deal_items.values_list("part_id", flat=True)
        for part_id in updated_parts:
            if int(part_id) not in existing_parts:
                part = get_object_or_404(Part, id=part_id)
                DealItem.objects.create(Deal=Deal, part=part)

        messages.success(request, "Deal updated successfully!")
        return redirect("edit_Deal", Deal_id=deal.id)  # Redirect back after saving

    return render(
        request,
        "tracker/edit_Deal.html",
        {"deal": deal, "deal_items": deal_items, "parts": Part.objects.all(), "customers": customers,
         "companies": companies},
    )


@staff_member_required
def edit_part(request, part_id):
    part = get_object_or_404(Part, id=part_id)

    if request.method == "POST":
        part.name = request.POST.get('name')
        part.part_type_id = request.POST.get('part_type')
        part.step_id = request.POST.get('step')
        part.is_complete = 'is_complete' in request.POST
        part.assigned_emp_id = request.POST.get('assigned_emp') or None
        part.customer_id = request.POST.get('customer')
        part.Deal_id = request.POST.get('Deal')
        part.estimated_completion = request.POST.get('estimated_completion') or None
        part.status = request.POST.get('status')
        part.save()
        return redirect('/edit_part/' + str(part.id))

    context = {
        'part': part,
        'part_types': PartType.objects.all(), 'steps': Step.objects.filter(part_model_id=part.part_type.id),
        'employees': User.objects.filter(groups__name='Employees'),
        'customers': User.objects.filter(groups__name='Customers'),
        'Deals': Deal.objects.all(),
        'status': Part.Status.values,
    }
    return render(request, 'tracker/edit_part.html', context)


def home(request):
    return render(request, 'tracker/home.html', {"current_time": timezone.localtime()})


def create_page(request):
    return render(request, 'tracker/create_page.html')


@method_decorator(staff_member_required, name='dispatch')
class GenericCreateEntry(CreateView):
    template_name = 'tracker/entry_form.html'

    def get_form_class(self):
        """Dynamically generate a ModelForm for the given model."""
        model_name = self.kwargs.get('model_name')
        model = apps.get_model("Tracker", model_name)  # Adjust 'Tracker' to match your app label

        if not model:
            raise Http404(f"Model '{model_name}' not found.")

        return modelform_factory(model, fields="__all__")  # Generates the form automatically

    def get_success_url(self):
        """Redirect after successful creation."""
        return reverse_lazy('create_page')  # Replace with your actual success URL

    def form_valid(self, form):
        return reverse_lazy(create_page)


class GenericUpdateEntry(UpdateView):
    template_name = 'tracker/update_form.html'

    def get_form_class(self):
        model_name = self.kwargs.get('model_name')
        model = apps.get_model("Tracker", model_name)

        if not model:
            raise Http404(f"Model '{model_name}' not found.")

        return modelform_factory(model, fields="__all__")

    def get_success_url(self):
        return reverse_lazy('edit')

    def get_queryset(self):
        model_name = self.kwargs.get('model_name')
        model = apps.get_model("Tracker", model_name)

        if not model:
            raise Http404(f"Model '{model_name}' not found.")

        # This assumes you're trying to fetch an object by its primary key.
        pk = self.kwargs.get('pk')
        return model.objects.filter(pk=pk)

    def form_valid(self, form):
        # Save the form data
        form.save()
        # Now redirect to the success URL (edit page)
        return redirect(self.get_success_url())


# TODO: This is gonna need some work
@method_decorator(login_required, name='dispatch')
class GenericDeleteEntry(DeleteView):
    template_name = 'tracker/delete.html'

    def get_delete_class(self):
        blocked_from_delete = ['part', 'deals']
        model_name = self.kwargs.get('model_name')
        if model_name in blocked_from_delete:
            raise Http404(f"Model '{model_name}' is not allowed to be deleted. Only archived.")
        if not model_name:
            raise Http404(f"Model '{model_name}' not found.")

@method_decorator(login_required, name='dispatch')
class GenericViewEntry(DetailView):
    template_name = 'tracker/generic_view.html'

    def get_model(self):
        """Helper method to get the model dynamically."""
        model_name = self.kwargs.get('model_name')
        model = apps.get_model("Tracker", model_name)
        if not model:
            raise Http404(f"Model '{model_name}' not found.")
        return model

    @method_decorator(login_required, name='dispatch')
    def get_queryset(self):
        model_name = self.kwargs.get('model_name')
        model = apps.get_model("Tracker", model_name)

        if not model:
            raise Http404(f"Model '{model_name}' not found.")

        # This assumes you're trying to fetch an object by its primary key.
        pk = self.kwargs.get('pk')
        return model.objects.filter(pk=pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        context["fields"] = [(field.verbose_name, getattr(obj, f"get_{field.name}_display", lambda: getattr(obj, field.name))()) for field in obj._meta.fields]
        return context

class qa_page(View):
    def get(self, request):
        context = {}
        parts = get_list_or_404(Part, archived=False)
        context["parts"] = parts
        return render(request, 'tracker/qa.html', context=context)

    def post(self, request, *args, **kwargs):
        part = get_object_or_404(Part, id=request.POST.get('part_id'))
        if request.POST["action"] == "Pass":
            part_step = part.step
            if part_step.is_last_step == True:
                part.status = 'COMPLETED'
            else:
                next_step = get_object_or_404(Step, part_model_id=request.POST.get('part_id'), step=part_step.step + 1)
                part.step = next_step
                part.step_id = next_step.id
                part.save()
            return redirect('QA')
        elif request.POST["action"] == "Error":
            return redirect('error_form', part_id=part.id)



def docs(request):
    return None


def single_doc(request, doc_id):
    return None


def error_form(request, part_id):
    part = get_object_or_404(Part, id=part_id)
    machines = Equipment.objects.all()
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
            machine = Equipment.objects.filter(id=machine_id)
            operator = User.objects.filter(first_name__in=[operator_name.split()[0]], last_name__in=[
                operator_name.split()[-1]]).first() if operator_name else None

            # Save the error report manually
            error_report = ErrorReport.objects.create(
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
def bulk_add_parts(request, deal_id):
    if request.method == "POST":
        x=0

        return redirect()

    else:
        return render(request, 'tracker/bulk_add.html')

@staff_member_required()
def bulk_operations(request):
    context = {}
    deals = get_list_or_404(Deal)
    context["deals"] = deals

    return render(request, 'tracker/bulk_operations.html', context=context)

@staff_member_required()
def bulk_edit(request, deal_id):
    context = {}
    deal = get_object_or_404(Deal, id=deal_id)
    context["deal"] = deal
    return render(request, 'tracker/bulk_edit.html', context=context)