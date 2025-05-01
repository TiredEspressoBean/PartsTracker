from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from Tracker.models import Companies, User, PartTypes, Processes, Steps, Deals, Parts, DealItems, PartDocs, Equipments, EquipmentsUsed, QualityErrorsList, ErrorReports, QualityErrorsOnParts
import random
from faker import Faker
from datetime import timedelta, datetime
from django.utils import timezone
from django.core.files.base import ContentFile

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
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                username=fake.user_name(),
                password="password",
                email=fake.company_email(),
                parent_company=random.choice(companies)
            )
            emp.groups.add(employees_group)
            employees.append(emp)

            cust = User.objects.create_user(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                username=fake.user_name(),
                password="password",
                email=fake.email(),
                parent_company=random.choice(companies)
            )
            cust.groups.add(customers_group)
            customers.append(cust)

        # Create PartTypes and Processes
        part_types = []
        for _ in range(5):
            pt = PartTypes.objects.create(
                name=fake.word().capitalize() + " Type",
                num_steps=random.randint(3, 6)
            )
            part_types.append(pt)

            # Create Processes for each PartType
            for _ in range(random.randint(1, 3)):  # random number of processes per part type
                Processes.objects.create(
                    name=fake.word().capitalize(),
                    is_remanufactured=random.choice([True, False]),
                    part_type=pt
                )

        # Create Steps for each Process
        for pt in part_types:
            processes = Processes.objects.filter(part_type=pt)
            for process in processes:
                for step_num in range(pt.num_steps):
                    Steps.objects.create(
                        step=step_num,
                        process=process,
                        description=fake.sentence(),
                        part_model=pt,
                        completion_time=(datetime.min + timedelta(minutes=random.randint(5, 60))).time(),
                        is_last_step=(step_num == pt.num_steps - 1)
                    )

        # Create Equipment
        equipment_list = [
            Equipments.objects.create(
                name=fake.word().capitalize(),
                equipmentType=random.choice(Equipments.EquipmentType.values)
            ) for _ in range(5)
        ]

        # Create Deals
        deals = [
            Deals.objects.create(
                name=fake.bs().capitalize(),
                customer=random.choice(customers),
                company=random.choice(companies),
                estimated_completion=fake.future_date(),
                status=random.choice(Deals.Status.values),
                hubspot_api_id=f"HS_DEAL_{i}",
                current_hubspot_gate=fake.word().upper(),
                archived=False
            ) for i in range(5)
        ]

        # Create Parts and related data
        for _ in range(10):
            pt = random.choice(part_types)
            deal = random.choice(deals)
            steps = Steps.objects.filter(part_model=pt).order_by('step')
            step = steps.first() if steps else None
            assigned_emp = random.choice(employees)
            customer = random.choice(customers)

            part = Parts.objects.create(
                name=fake.word().capitalize() + " Part",
                glovia_id=fake.uuid4()[:8].upper(),
                part_type=pt,
                step=step,
                assigned_emp=assigned_emp,
                customer=customer,
                deal=deal,
                estimated_completion=fake.future_date(),
                status=random.choice(Parts.Status.values),
                archived=False
            )

            # DealItem
            DealItems.objects.create(deal=deal, part=part)

            # PartDoc
            PartDocs.objects.create(
                is_image=random.choice([True, False]),
                part_step=step.step if step else 0,
                file_name="example.txt",
                file=ContentFile(b"Sample file content.", name="example.txt"),
                uploaded_by=assigned_emp,
                part_type=pt
            )

            # EquipmentUsed
            EquipmentsUsed.objects.create(
                equipment=random.choice(equipment_list),
                step=step,
                part=part
            )

            # ErrorReport
            error_report = ErrorReports.objects.create(
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
