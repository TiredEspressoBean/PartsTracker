from django import forms
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.forms import modelform_factory
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.apps import apps


@method_decorator(staff_member_required, name='dispatch')
class GenericCreateEntry(CreateView):
    template_name = 'tracker/generic_create.html'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        for field_name, field in form.fields.items():
            existing_classes = map_generic_form_input_styles(field)
            field.widget.attrs['class'] = existing_classes
        return form

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
        # Save the form and model instance
        self.object = form.save()

        # Handle form session management
        next_form = self.get_next_form_from_session()  # Custom logic to get the next form

        if next_form:
            # Proceed to the next form
            return redirect(next_form)  # Or whatever your redirect logic is
        else:
            # If no more forms, finish the wizard
            return HttpResponseRedirect(self.get_success_url())


class GenericUpdateEntry(UpdateView):
    template_name = 'tracker/generic_update.html'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        for field_name, field in form.fields.items():
            existing_classes = map_generic_form_input_styles(field)
            field.widget.attrs['class'] = existing_classes
        return form

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
    template_name = 'tracker/generic_delete.html'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        for field_name, field in form.fields.items():
            existing_classes = map_generic_form_input_styles(field)
            field.widget.attrs['class'] = existing_classes
        return form

    def get_queryset(self):
        model = self.get_model()
        pk = self.kwargs.get('pk')
        return model.objects.filter(pk=pk)

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
        model_name = self.kwargs.get('model_name')
        model = apps.get_model("Tracker", model_name)
        if not model:
            raise Http404(f"Model '{model_name}' not found.")
        return model

    def get_queryset(self):
        model = self.get_model()
        pk = self.kwargs.get('pk')
        return model.objects.filter(pk=pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        context["fields"] = [
            (field.verbose_name, getattr(obj, f"get_{field.name}_display", lambda: getattr(obj, field.name))())
            for field in obj._meta.fields
        ]
        return context


def map_generic_form_input_styles(field, fieldtype=None):
    """
    Apply Tailwind-compatible classes to a Django form field based on its type.
    Optionally accepts `fieldtype` to override autodetection.
    """
    fieldtype = fieldtype or type(field)

    classes = ""

    base_input_class = "rounded-md border border-gray-300 shadow-sm focus:outline-none"

    type_class_map = {
        forms.CharField: f"{base_input_class} focus:border-green-500 focus:ring focus:ring-blue-500 focus:ring-opacity-50 m-1 m-1.5",
        forms.IntegerField: f"{base_input_class} max-w-sm focus:border-yellow-500 focus:ring focus:ring-yellow-500 focus:ring-opacity-50 m-1.5",
        forms.FloatField: f"{base_input_class} focus:border-yellow-500 focus:ring focus:ring-yellow-500 focus:ring-opacity-50 m-1.5",
        forms.BooleanField: "h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500 m-1.5",
        forms.DateField: f"{base_input_class} focus:border-green-500 focus:ring focus:ring-green-500 focus:ring-opacity-50 m-1.5",
        forms.DateTimeField: f"{base_input_class} focus:border-green-500 focus:ring focus:ring-green-500 focus:ring-opacity-50 m-1.5",
        forms.EmailField: f"{base_input_class} focus:border-purple-500 focus:ring focus:ring-purple-500 focus:ring-opacity-50 m-1.5",
        forms.URLField: f"{base_input_class} focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50 m-1.5",
        forms.TimeField: f"{base_input_class} focus:border-pink-500 focus:ring focus:ring-pink-500 focus:ring-opacity-50 m-1.5",
        forms.ChoiceField: f"{base_input_class} focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50 m-1.5",
        forms.TypedChoiceField: f"{base_input_class} focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50 m-1.5",
        forms.ModelChoiceField: f"{base_input_class} focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50 m-1.5",
        forms.Textarea: f"{base_input_class} focus:border-blue-500 focus:ring focus:ring-blue-500 focus:ring-opacity-50 m-1.5",
        forms.FileField: "block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 m-1.5",
    }

    # Match via subclass (e.g., a custom MyIntegerField)
    for base_type, css_classes in type_class_map.items():
        if isinstance(field, base_type):
            classes = css_classes
        else:
            f"{base_input_class} focus:border-blue-500 focus:ring focus:ring-blue-500 focus:ring-opacity-50"
    if field and field.required:
        classes += " after:content-['*'] after:ml-0.5 after:text-red-500"

    return classes



def apply_styles_to_form(form):
    for field in form.fields.values():
        field.widget.attrs['class'] = map_generic_form_input_styles(field)

def apply_styles_to_formset(formset):
    for form in formset:
        apply_styles_to_form(form)