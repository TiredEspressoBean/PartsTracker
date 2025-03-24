from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_list_or_404, get_object_or_404
from django.utils import timezone
from django.utils.timezone import now

from Tracker.models import Part, Deal, DealItem, PartType, Step, User


# Create your views here.


def tracker(request):
    context = {}
    user = request.user
    if user.is_authenticated:
        if user.is_staff:
            parts = get_list_or_404(Part)
            context.update({'parts': parts})
            # Get rid of this part once I have a tester customer for the DB
            orders = get_list_or_404(Order)
            context.update({'orders': orders})
        else:
            orders = get_list_or_404(Order, customer=user)
            context.update({'orders': orders})
            parts = get_list_or_404(Part, customer=user)
            context.update({'parts': parts})
    return render(request, template_name='tracker/tracker.html', context=context)


def upload(request):
    return None


@login_required
def part_view(request, part_id):
    context = {}
    part = get_object_or_404(Part, id=part_id)
    context.update({'part': part})
    return render(request, 'tracker/part_view.html', context=context)

@login_required
def order_view(request, order_id):
    context = {}
    order = get_object_or_404(Order, id=order_id)
    context.update({'order': order})
    return render(request, 'tracker/order_view.html', context=context)


@staff_member_required
def edit(request):
    context = {}
    parts = get_list_or_404(Part)
    for part in parts:
        order = get_object_or_404(Order, id=part.order_id)
        part.customer = order.customer
    orders = get_list_or_404(Order)
    context.update({'parts': parts})
    context.update({'orders': orders})
    return render(request, 'tracker/edit.html', context=context)


@staff_member_required
def edit_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order_items = OrderItem.objects.filter(order=order)
    customers = get_list_or_404(User, groups__name='Customers')

    if request.method == "POST":
        # Update Order Fields
        order.customer_id = request.POST.get("customer")
        order.estimated_completion = request.POST.get("estimated_delivery")
        order.save()

        # Update Order Items
        updated_parts = request.POST.getlist("order_items")  # Get all selected parts

        # Remove any items that were not included in the form
        order_items.exclude(part_id__in=updated_parts).delete()

        # Add new items if necessary
        existing_parts = order_items.values_list("part_id", flat=True)
        for part_id in updated_parts:
            if int(part_id) not in existing_parts:
                part = get_object_or_404(Part, id=part_id)
                OrderItem.objects.create(order=order, part=part)

        messages.success(request, "Order updated successfully!")
        return redirect("edit_order", order_id=order.id)  # Redirect back after saving

    return render(
        request,
        "tracker/edit_order.html",
        {"order": order, "order_items": order_items, "parts": Part.objects.all(), "customers": customers},
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
        part.order_id = request.POST.get('order')
        part.estimated_completion = request.POST.get('estimated_completion') or None
        part.status = request.POST.get('status')
        part.save()
        return redirect('/edit_part/' + str(part.id))

    context = {
        'part': part,
        'part_types': PartType.objects.all(),        'steps': Step.objects.filter(part_model_id=part.part_type.id),
        'employees': User.objects.filter(groups__name='Employees'),
        'customers': User.objects.filter(groups__name='Customers'),
        'orders': Order.objects.all(),
        'status': Part.Status.values,
    }
    return render(request, 'tracker/edit_part.html', context)


def home(request):
    return render(request, 'tracker/home.html', {"current_time": timezone.localtime()})


def docs(request):
    return None


def doc(request, doc_id):
    return None