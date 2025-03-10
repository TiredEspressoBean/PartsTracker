from datetime import time, timedelta

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


# Create your models here.
class PartType(models.Model):
    name = models.CharField(max_length=50)
    num_steps = models.IntegerField()


class Step(models.Model):
    step = models.IntegerField()
    description = models.TextField()
    part_model = models.ForeignKey(PartType, on_delete=models.CASCADE)
    completion_time = models.TimeField()

    class Meta:
        ordering = ('part_model', 'step',)


class User(AbstractUser):
    date_joined = models.DateTimeField(default=timezone.now)
    company = models.CharField(max_length=150)


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', "Pending"
        IN_PROGRESS = 'IN_PROGRESS', "In progress"
        COMPLETED = 'COMPLETED', "Completed"
        ON_HOLD = 'ON_HOLD', "On hold"
        CANCELLED = 'CANCELLED', "Cancelled"

    name = models.CharField(max_length=50)
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    estimated_completion = models.DateField(null=True)
    status = models.CharField(max_length=50, choices=Status.choices, default=Status.PENDING)


class Part(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', "Pending"
        IN_PROGRESS = 'IN_PROGRESS', "In progress"
        COMPLETED = 'COMPLETED', "Completed"
        ON_HOLD = 'ON_HOLD', "On hold"
        CANCELLED = 'CANCELLED', "Cancelled"

    name = models.CharField(max_length=50)
    part_type = models.ForeignKey(PartType, on_delete=models.SET_NULL, null=True)
    step = models.ForeignKey(Step, on_delete=models.SET_NULL, null=True)
    assigned_emp = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigned_emp')
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='customer')
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    estimated_completion = models.DateField(null=True)
    status = models.CharField(max_length=50, choices=Status.choices, default=Status.PENDING)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    part = models.ForeignKey(Part, on_delete=models.CASCADE)


class PartDoc(models.Model):
    is_image = models.BooleanField()
    part_step = models.IntegerField()
    file_name = models.CharField(max_length=50)
    file = models.FileField(upload_to='parts_docs/')
    upload_date = models.DateField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    part_type = models.ForeignKey(PartType, on_delete=models.SET_NULL, null=True)
