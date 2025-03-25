from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.decorators import login_required
from django.forms import modelform_factory
from django.http import Http404
from django.shortcuts import render, redirect, get_list_or_404, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.timezone import now
from django.views.generic import CreateView
from django.views.generic.detail import DetailView
from django.apps import apps

from Tracker.models import Part, Deal, DealItem, PartType, Step, User, Companies


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
    company = get_object_or_404(Companies, id=customer.id)
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
    deal_items = get_list_or_404(DealItem, deal_id=deal_id)
    deal_parts = []
    for part in deal_items:
        deal_parts.extend(Part.objects.filter(id=part.id))
    context.update({'deal_parts': deal_parts})

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

    def get_success_url(self):
        """Redirect after successful creation."""
        return reverse_lazy('create_page')

    def form_valid(self, form):
        return reverse_lazy(create_page)


def docs(request):
    return None


def doc(request, doc_id):
    return None
