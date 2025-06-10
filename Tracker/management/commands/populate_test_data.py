from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from Tracker.models import (
    Companies, User, PartTypes, Processes, Steps, Orders, Parts, Documents,
    Equipments, EquipmentType, QualityErrorsList, ErrorReports,
    EquipmentUsage, ArchiveReason, StepTransitionLog
)
import random
from faker import Faker
from datetime import timedelta
from django.utils import timezone
from django.core.files.base import ContentFile

class Command(BaseCommand):
    help = "Generate realistic test data for diesel fuel injector manufacturing"

    def handle(self, *args, **kwargs):
        fake = Faker()

        # Create user groups
        employees_group, _ = Group.objects.get_or_create(name='employee')
        customers_group, _ = Group.objects.get_or_create(name='customer')
        managers_group, _ = Group.objects.get_or_create(name='manager')

        # Create companies
        companies = [
            Companies.objects.create(
                name=f"{fake.company()} Diesel Systems",
                description=fake.catch_phrase(),
                hubspot_api_id=f"HS_COMP_{i}"
            ) for i in range(3)
        ]

        # Create users
        employees, customers, managers = [], [], []
        for _ in range(3):
            emp = User.objects.create_user(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                username=fake.unique.user_name(),
                password="password",
                email=fake.company_email(),
                parent_company=random.choice(companies)
            )
            emp.groups.add(employees_group)
            employees.append(emp)

            cust = User.objects.create_user(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                username=fake.unique.user_name(),
                password="password",
                email=fake.email(),
                parent_company=random.choice(companies)
            )
            cust.groups.add(customers_group)
            customers.append(cust)

            mgr = User.objects.create_user(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                username=fake.unique.user_name(),
                password="password",
                email=fake.company_email(),
                parent_company=random.choice(companies)
            )
            mgr.groups.add(managers_group)
            managers.append(mgr)

        # Create equipment types and equipment
        eq_types = [EquipmentType.objects.create(name=et) for et in ["Assembly Rig", "Test Bench", "Seal Station"]]
        equipment_list = [
            Equipments.objects.create(
                name=f"EQ-{fake.random_int(100, 999)}",
                equipment_type=random.choice(eq_types)
            ) for _ in range(5)
        ]

        # Create part types and processes
        part_types = []
        for _ in range(3):
            pt = PartTypes.objects.create(
                name=fake.word().capitalize() + " Injector",
                ID_prefix="DI"
            )
            part_types.append(pt)

            for _ in range(2):
                proc = Processes.objects.create(
                    name=fake.word().capitalize(),
                    is_remanufactured=random.choice([True, False]),
                    part_type=pt,
                    num_steps=3
                )
                proc.generate_steps()

        # Create orders
        orders = [
            Orders.objects.create(
                name=f"Batch-{fake.word().capitalize()}",
                customer=random.choice(customers),
                company=random.choice(companies),
                estimated_completion=timezone.now().date() + timedelta(days=random.randint(2, 10)),
                status=random.choice([s[0] for s in Orders.Status.choices]),
                current_hubspot_gate=fake.word().upper(),
                archived=False
            ) for _ in range(5)
        ]

        # Add archived orders
        for reason_key, note in [
            ("completed", "Order successfully fulfilled."),
            ("user_error", "Input error in original order details."),
            ("obsolete", "Order cancelled due to product revision.")
        ]:
            order = Orders.objects.create(
                name=f"Archived-{fake.word().capitalize()}",
                customer=random.choice(customers),
                company=random.choice(companies),
                estimated_completion=timezone.now().date() - timedelta(days=random.randint(5, 20)),
                status=Orders.Status.CANCELLED,
                current_hubspot_gate=fake.word().upper(),
                archived=True
            )
            ArchiveReason.objects.create(
                reason=reason_key,
                notes=note,
                content_object=order,
                user=random.choice(employees)
            )
            # Attach a part and archive it too
            pt = random.choice(part_types)
            processes = pt.processes.all()
            if not processes:
                continue
            process = random.choice(processes)
            steps = process.steps.all().order_by('step')
            if not steps:
                continue
            step = steps.first()
            part = Parts.objects.create(
                ERP_id=fake.uuid4().split('-')[0].upper(),
                part_type=pt,
                step=step,
                order=order,
                status=Parts.Status.CANCELLED,
                archived=True
            )
            ArchiveReason.objects.create(
                reason=reason_key,
                notes=f"Part archived with order for reason: {note}",
                content_object=part,
                user=random.choice(employees)
            )

        # Create parts, docs, errors, usage logs, and transition logs
        for _ in range(10):
            pt = random.choice(part_types)
            order = random.choice(orders)
            processes = pt.processes.all()
            if not processes:
                continue
            process = random.choice(processes)
            steps = process.steps.all().order_by('step')
            if not steps:
                continue
            step = steps.first()

            part = Parts.objects.create(
                ERP_id=fake.uuid4().split('-')[0].upper(),
                part_type=pt,
                step=step,
                order=order,
                status=random.choice([s[0] for s in Parts.Status.choices]),
                archived=False
            )

            # Upload part doc
            Documents.objects.create(
                is_image=random.choice([True, False]),
                file_name="example.txt",
                file=ContentFile(b"Sample file content.", name="example.txt"),
                uploaded_by=random.choice(employees),
                part=part
            )

            # Equipment usage
            EquipmentUsage.objects.create(
                equipment=random.choice(equipment_list),
                step=step,
                part=part,
                operator=random.choice(employees),
                notes="Simulated usage"
            )

            # Error reporting
            error_report = ErrorReports.objects.create(
                part=part,
                machine=random.choice(equipment_list),
                operator=random.choice(employees),
                description=fake.text(max_nb_chars=300)
            )
            error_list = [
                QualityErrorsList.objects.create(
                    error_name=fake.catch_phrase(),
                    error_example=fake.sentence(),
                    part_type=pt
                ) for _ in range(random.randint(1, 2))
            ]
            error_report.errors.set(error_list)

            # Step transition log
            for s in steps:
                StepTransitionLog.objects.create(
                    step=s,
                    part=part,
                    operator=random.choice(employees),
                    timestamp=timezone.now() - timedelta(hours=random.randint(1, 48))
                )

        self.stdout.write(self.style.SUCCESS("✅ Sample manufacturing data populated successfully."))
