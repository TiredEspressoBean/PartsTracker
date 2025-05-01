import json
import uuid
from collections import OrderedDict

from django.urls import reverse_lazy
from formtools.wizard.views import SessionWizardView
from django import forms
from django.apps import apps
from django.forms import modelformset_factory, formset_factory
from django.shortcuts import redirect

from Tracker.generic_views import map_generic_form_input_styles, apply_styles_to_form
from Tracker.models import Parts, Deals, DealItems, Processes, PartTypes, PartDocs


class PartsFormforDeals(forms.ModelForm):

    estimated_completion = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    class Meta:
        model = Parts
        exclude = ['deal', 'customer', 'archived']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            css_classes = map_generic_form_input_styles(field)

            if "class" in field.widget.attrs:
                field.widget.attrs["class"] += f" {css_classes}"
            else:
                field.widget.attrs["class"] = css_classes


class DealForm(forms.ModelForm):
    estimated_completion = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    required_css_class = "after:content-['*'] after:text-red-600 after:ml-2 after:text-2xl"
    class Meta:
        model = Deals
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            css_classes = map_generic_form_input_styles(field)

            if "class" in field.widget.attrs:
                field.widget.attrs["class"] += f" {css_classes}"
            else:
                field.widget.attrs["class"] = css_classes



class ProcessForm(forms.ModelForm):
    class Meta:
        model = Processes
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            css_classes = map_generic_form_input_styles(field)
            if "class" in field.widget.attrs:
                field.widget.attrs["class"] += f" {css_classes}"
            else:
                field.widget.attrs["class"] = css_classes

class PartTypeForm(forms.ModelForm):
    class Meta:
        model = PartTypes
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            css_classes = map_generic_form_input_styles(field)
            if "class" in field.widget.attrs:
                field.widget.attrs["class"] += f" {css_classes}"
            else:
                field.widget.attrs["class"] = css_classes

class LineItemForm(forms.Form):
    quantity = forms.IntegerField(min_value=1)
    part_type = forms.ModelChoiceField(queryset=PartTypes.objects.all(), required=False)
    enumeration_start = forms.IntegerField(min_value=1)
    process = forms.ModelChoiceField(queryset=Processes.objects.all(), required=False)


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Define the base form control classes (your Tailwind input style)
        input_classes = map_generic_form_input_styles(None)

        # Apply CSS and special attributes per field
        for name, field in self.fields.items():
            css_classes = map_generic_form_input_styles(field)
            if "class" in field.widget.attrs:
                field.widget.attrs["class"] += f" {input_classes}"
            else:
                field.widget.attrs["class"] = input_classes

        # HTMX dynamic swap setup for part_type
        self.fields['part_type'].widget.attrs.update({
            'hx-get': reverse_lazy('parttype_select_partial'),
            'hx-trigger': 'refresh-parttypes from:body',
            'hx-target': 'this',
            'hx-swap': 'innerHTML',
            'class': input_classes,   # <-- Make sure it REAPPLIES classes after swap
        })

        # HTMX dynamic swap setup for process
        self.fields['process'].widget.attrs.update({
            'hx-get': reverse_lazy('process_select_partial'),
            'hx-trigger': 'refresh-processes from:body',
            'hx-target': 'this',
            'hx-swap': 'innerHTML',
            'class': input_classes,   # <-- same here
        })

        for field_name, field in self.fields.items():
            css_classes = map_generic_form_input_styles(field)
            if "class" in field.widget.attrs:
                field.widget.attrs["class"] += f" {css_classes}"
            else:
                field.widget.attrs["class"] = css_classes




LineItemFormSet = formset_factory(
    LineItemForm,
    extra=1,
    can_delete=True
)

class PartDocForm(forms.ModelForm):
    class Meta:
        model = PartDocs
        fields = ['is_image', 'file_name', 'file', 'part']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            css_classes = map_generic_form_input_styles(field)
            if "class" in field.widget.attrs:
                field.widget.attrs["class"] += f" {css_classes}"
            else:
                field.widget.attrs["class"] = css_classes