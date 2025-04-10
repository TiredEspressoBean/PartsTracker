from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class PartType(models.Model):
    name = models.CharField(max_length=50)
    num_steps = models.IntegerField()
    remanufactured = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Step(models.Model):
    step = models.IntegerField()
    description = models.TextField()
    part_model = models.ForeignKey(PartType, on_delete=models.CASCADE)
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


class User(AbstractUser):
    date_joined = models.DateTimeField(default=timezone.now)
    parent_company = models.ForeignKey(Companies, on_delete=models.SET_NULL, null=True, blank=True, default=None)


class Deal(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', "Pending"
        IN_PROGRESS = 'IN_PROGRESS', "In progress"
        COMPLETED = 'COMPLETED', "Completed"
        ON_HOLD = 'ON_HOLD', "On hold"
        CANCELLED = 'CANCELLED', "Cancelled"

    name = models.CharField(max_length=50)
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    company = models.ForeignKey(Companies, on_delete=models.SET_NULL, null=True)
    estimated_completion = models.DateField(null=True)
    status = models.CharField(max_length=50, choices=Status.choices, default=Status.PENDING)
    hubspot_api_id = models.CharField(max_length=50)
    current_hubspot_gate = models.CharField(max_length=50)
    archived = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Part(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', "Pending"
        IN_PROGRESS = 'IN_PROGRESS', "In progress"
        COMPLETED = 'COMPLETED', "Completed"
        ON_HOLD = 'ON_HOLD', "On hold"
        CANCELLED = 'CANCELLED', "Cancelled"

    name = models.CharField(max_length=50)
    glovia_id = models.CharField(max_length=50)
    part_type = models.ForeignKey(PartType, on_delete=models.SET_NULL, null=True)
    step = models.ForeignKey(Step, on_delete=models.SET_NULL, null=True)
    assigned_emp = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigned_emp')
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='customer')
    deal = models.ForeignKey(Deal, on_delete=models.CASCADE)
    estimated_completion = models.DateField(null=True)
    status = models.CharField(max_length=50, choices=Status.choices, default=Status.PENDING)
    archived = models.BooleanField(default=False)


class DealItem(models.Model):
    deal = models.ForeignKey(Deal, related_name="items", on_delete=models.CASCADE)
    part = models.ForeignKey(Part, on_delete=models.CASCADE)


class PartDoc(models.Model):
    is_image = models.BooleanField()
    part_step = models.IntegerField()
    file_name = models.CharField(max_length=50)
    file = models.FileField(upload_to='parts_docs/')
    upload_date = models.DateField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    part_type = models.ForeignKey(PartType, on_delete=models.SET_NULL, null=True)


class Equipment(models.Model):
    name = models.CharField(max_length=50)

    class EquipmentType(models.TextChoices):
        Unassigned = "Unassigned", "Unassigned"
        ASSEMBLER = 'ASSEMBLER', "Assembler"

    equipmentType = models.CharField(max_length=50, choices=EquipmentType.choices, default=EquipmentType.Unassigned)


class EquipmentUsed(models.Model):
    equipment = models.ForeignKey(Equipment, on_delete=models.SET_NULL, null=True)
    step = models.ForeignKey(Step, on_delete=models.SET_NULL, null=True)
    part = models.ForeignKey(Part, on_delete=models.SET_NULL, null=True)


class QualityErrorsList(models.Model):
    error_name = models.CharField(max_length=50)
    error_example = models.TextField()
    part_type = models.ForeignKey(PartType, on_delete=models.SET_NULL, null=True)


class ErrorReport(models.Model):
    part = models.ForeignKey("Part", on_delete=models.SET_NULL, null=True, related_name="error_reports")
    machine = models.ForeignKey("Equipment", on_delete=models.SET_NULL, null=True, blank=True)
    operator = models.ForeignKey("User", on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(max_length=300)
    file = models.FileField(upload_to="error_reports/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class QualityErrorsOnParts(models.Model):
    error_id = models.ForeignKey(QualityErrorsList, on_delete=models.SET_NULL, null=True)
    part_with_error = models.ForeignKey(Part, on_delete=models.SET_NULL, null=True)
    error_report = models.ForeignKey(ErrorReport, on_delete=models.SET_NULL, null=True)
