from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from Tracker.models import Companies, User, Part, PartType, Deal, Step, DealItem, PartDoc, Equipment, EquipmentUsed, QualityErrorsList, ErrorReport, QualityErrorsOnParts
import random
from faker import Faker
from datetime import timedelta, datetime
from django.utils import timezone
from django.core.files.base import ContentFile
import io

class Command(BaseCommand):
    help = "Generate sample data for development"

    def handle(self, *args, **kwargs):
        fake = Faker()

        # Create groups
        employees_group, _ = Group.objects.get_or_create(name='employee')
        customers_group, _ = Group.objects.get_or_create(name='customer')

        # Create companies
        companies = [
            Companies.objects.create(
                name=fake.company(),
                description=fake.catch_phrase(),
                hubspot_api_id=f"HS_COMP_{i}"
            ) for i in range(5)
        ]

        # Create users
        employees, customers = [], []
        for _ in range(5):
            emp = User.objects.create_user(
                username=fake.user_name(),
                password="password",
                email=fake.company_email(),
                parent_company=random.choice(companies)
            )
            emp.groups.add(employees_group)
            employees.append(emp)

            cust = User.objects.create_user(
                username=fake.user_name(),
                password="password",
                email=fake.email(),
                parent_company=random.choice(companies)
            )
            cust.groups.add(customers_group)
            customers.append(cust)

        # Create PartTypes and Steps
        part_types = []
        for _ in range(5):
            pt = PartType.objects.create(
                name=fake.word().capitalize() + " Type",
                num_steps=random.randint(3, 6),
                remanufactured=random.choice([True, False])
            )
            for step_num in range(pt.num_steps):
                Step.objects.create(
                    step=step_num,
                    description=fake.sentence(),
                    part_model=pt,
                    completion_time=(datetime.min + timedelta(minutes=random.randint(5, 60))).time(),
                    is_last_step=(step_num == pt.num_steps - 1)
                )
            part_types.append(pt)

        # Create Equipment
        equipment_list = [
            Equipment.objects.create(
                name=fake.word().capitalize(),
                equipmentType=random.choice(Equipment.EquipmentType.values)
            ) for _ in range(5)
        ]

        # Create Deals
        deals = [
            Deal.objects.create(
                name=fake.bs().capitalize(),
                customer=random.choice(customers),
                company=random.choice(companies),
                estimated_completion=fake.future_date(),
                status=random.choice(Deal.Status.values),
                hubspot_api_id=f"HS_DEAL_{i}",
                current_hubspot_gate=fake.word().upper(),
                archived=False
            ) for i in range(5)
        ]

        # Create Parts and related data
        for _ in range(10):
            pt = random.choice(part_types)
            deal = random.choice(deals)
            steps = Step.objects.filter(part_model=pt).order_by('step')
            step = steps.first() if steps else None
            assigned_emp = random.choice(employees)
            customer = random.choice(customers)

            part = Part.objects.create(
                name=fake.word().capitalize() + " Part",
                glovia_id=fake.uuid4()[:8].upper(),
                part_type=pt,
                step=step,
                assigned_emp=assigned_emp,
                customer=customer,
                deal=deal,
                estimated_completion=fake.future_date(),
                status=random.choice(Part.Status.values),
                archived=False
            )

            # DealItem
            DealItem.objects.create(deal=deal, part=part)

            # PartDoc
            PartDoc.objects.create(
                is_image=random.choice([True, False]),
                part_step=step.step if step else 0,
                file_name="example.txt",
                file=ContentFile(b"Sample file content.", name="example.txt"),
                uploaded_by=assigned_emp,
                part_type=pt
            )

            # EquipmentUsed
            EquipmentUsed.objects.create(
                equipment=random.choice(equipment_list),
                step=step,
                part=part
            )

            # ErrorReport
            error_report = ErrorReport.objects.create(
                part=part,
                machine=random.choice(equipment_list),
                operator=assigned_emp,
                description=fake.text(max_nb_chars=300)
            )

            # QualityErrorsList
            error_type = QualityErrorsList.objects.create(
                error_name=fake.catch_phrase(),
                error_example=fake.sentence(),
                part_type=pt
            )

            # QualityErrorsOnParts
            QualityErrorsOnParts.objects.create(
                error_id=error_type,
                part_with_error=part,
                error_report=error_report
            )

        self.stdout.write(self.style.SUCCESS("✅ Successfully generated realistic sample data."))