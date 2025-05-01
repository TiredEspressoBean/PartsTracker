from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class PartTypes(models.Model):
    name = models.CharField(max_length=50)
    ID_prefix = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.name


class Processes(models.Model):
    name = models.CharField(max_length=50)
    is_remanufactured = models.BooleanField()
    num_steps = models.IntegerField()
    part_type = models.ForeignKey(PartTypes, on_delete=models.CASCADE)

    def __str__(self):
        return self.name + " " + str(self.part_type) + (" Reman" if self.is_remanufactured else "")


class Steps(models.Model):
    step = models.IntegerField()
    process = models.ForeignKey(Processes, on_delete=models.CASCADE)
    description = models.TextField()
    part_model = models.ForeignKey(PartTypes, on_delete=models.CASCADE)
    completion_time = models.TimeField()
    # TODO: Update with nomenclature within the business
    step_file = models.FileField(null=True, default=None)
    is_last_step = models.BooleanField(default=False)

    def __str__(self):
        return self.part_model.name + " " + str(self.step)

    class Meta:
        ordering = ('part_model', 'step',)


class Companies(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    hubspot_api_id = models.CharField(max_length=50)
    def __str__(self):
        return self.name


class User(AbstractUser):
    date_joined = models.DateTimeField(default=timezone.now)
    parent_company = models.ForeignKey(Companies, on_delete=models.SET_NULL, null=True, blank=True, default=None)
    def __str__(self):
        return self.username + ":" + " " + self.first_name + " " + self.last_name


class Deals(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', "Pending"
        IN_PROGRESS = 'IN_PROGRESS', "In progress"
        COMPLETED = 'COMPLETED', "Completed"
        ON_HOLD = 'ON_HOLD', "On hold"
        CANCELLED = 'CANCELLED', "Cancelled"

    name = models.CharField(max_length=50)
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    company = models.ForeignKey(Companies, on_delete=models.SET_NULL, null=True)
    estimated_completion = models.DateField(null=True, blank=True, auto_now_add=False)
    status = models.CharField(max_length=50, choices=Status.choices, default=Status.PENDING)
    hubspot_api_id = models.CharField(max_length=50, blank=True)
    current_hubspot_gate = models.CharField(max_length=50, blank=True)
    archived = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Parts(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', "Pending"
        IN_PROGRESS = 'IN_PROGRESS', "In progress"
        COMPLETED = 'COMPLETED', "Completed"
        ON_HOLD = 'ON_HOLD', "On hold"
        CANCELLED = 'CANCELLED', "Cancelled"

    glovia_id = models.CharField(max_length=50)
    part_type = models.ForeignKey(PartTypes, on_delete=models.SET_NULL, null=True)
    step = models.ForeignKey(Steps, on_delete=models.SET_NULL, null=True)
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='customer')
    deal = models.ForeignKey(Deals, on_delete=models.CASCADE)
    estimated_completion = models.DateField(null=True)
    status = models.CharField(max_length=50, choices=Status.choices, default=Status.PENDING)
    archived = models.BooleanField(default=False)

    def __str__(self):
        # Safely access the customer username with a fallback value if customer is None
        customer_username = getattr(self.customer, 'username', 'Unknown Customer') if self.customer else 'Unknown Customer'

        # Safely access the deal name with a fallback value if deal is None
        deal_name = getattr(self.deal, 'name', 'Unknown Deal') if self.deal else 'Unknown Deal'

        # Safely access the part type name with a fallback value if part_type is None
        part_type_name = getattr(self.part_type, 'name', 'Unknown Part Type') if self.part_type else 'Unknown Part Type'

        return f"{part_type_name} {self.glovia_id} {customer_username} {deal_name}"

class DealItems(models.Model):
    deal = models.ForeignKey(Deals, related_name="items", on_delete=models.CASCADE)
    part = models.ForeignKey(Parts, on_delete=models.CASCADE)


class PartDocs(models.Model):
    is_image = models.BooleanField()
    file_name = models.CharField(max_length=50)
    file = models.FileField(upload_to='parts_docs/')
    upload_date = models.DateField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    part = models.ForeignKey(Parts, on_delete=models.SET_NULL, null=True)


class Equipments(models.Model):
    name = models.CharField(max_length=50)

    class EquipmentType(models.TextChoices):
        Unassigned = "Unassigned", "Unassigned"
        ASSEMBLER = 'ASSEMBLER', "Assembler"

    equipmentType = models.CharField(max_length=50, choices=EquipmentType.choices, default=EquipmentType.Unassigned)


class EquipmentsUsed(models.Model):
    # TODO: I'm not sure this is best, maybe should be relational table tying the error report to the equipment in
    #  question
    equipment = models.ForeignKey(Equipments, on_delete=models.SET_NULL, null=True)
    step = models.ForeignKey(Steps, on_delete=models.SET_NULL, null=True)
    part = models.ForeignKey(Parts, on_delete=models.SET_NULL, null=True)


class QualityErrorsList(models.Model):
    error_name = models.CharField(max_length=50)
    error_example = models.TextField()
    part_type = models.ForeignKey(PartTypes, on_delete=models.SET_NULL, null=True)


class ErrorReports(models.Model):
    part = models.ForeignKey(Parts, on_delete=models.SET_NULL, null=True, related_name="error_reports")
    machine = models.ForeignKey(Equipments, on_delete=models.SET_NULL, null=True, blank=True)
    operator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(max_length=300)
    file = models.FileField(upload_to="error_reports/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class QualityErrorsOnParts(models.Model):
    error_id = models.ForeignKey(QualityErrorsList, on_delete=models.SET_NULL, null=True)
    part_with_error = models.ForeignKey(Parts, on_delete=models.SET_NULL, null=True)
    error_report = models.ForeignKey(ErrorReports, on_delete=models.SET_NULL, null=True)
