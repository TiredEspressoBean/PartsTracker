import random
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from Tracker.models import PartType, Step, User, Order, Part, PartDoc, OrderItem


class Command(BaseCommand):
    help = "Populates the database with test data"

    def handle(self, *args, **kwargs):
        self.stdout.write("🚀 Populating database with test data...")

        # Create Users
        users = list(User.objects.bulk_create([
            User(username=f"user_{i}", password="test123", company=f"Company_{i}")
            for i in range(5)
        ]))
        self.stdout.write(self.style.SUCCESS(f"✅ Created {len(users)} users"))

        # Create Part Types
        part_types = list(PartType.objects.bulk_create([
            PartType(name=f"PartType_{i}", num_steps=random.randint(2, 5))
            for i in range(3)
        ]))
        self.stdout.write(self.style.SUCCESS(f"✅ Created {len(part_types)} part types"))

        # Create Steps
        steps = []
        for part_type in part_types:
            steps.extend(Step.objects.bulk_create([
                Step(
                    step=i + 1,
                    description=f"Step {i + 1} for {part_type.name}",
                    part_model=part_type,
                    completion_time="12:00:00"  # Arbitrary time
                ) for i in range(part_type.num_steps)
            ]))
        self.stdout.write(self.style.SUCCESS(f"✅ Created {len(steps)} steps"))

        # Create Orders
        orders = list(Order.objects.bulk_create([
            Order(
                name=f"Order_{i}",
                customer=random.choice(users),
                is_complete=random.choice([True, False]),
                estimated_completion=date.today() + timedelta(days=random.randint(5, 20))
            ) for i in range(5)
        ]))
        self.stdout.write(self.style.SUCCESS(f"✅ Created {len(orders)} orders"))

        # Create Parts
        parts = []
        for order in orders:
            for _ in range(random.randint(1, 3)):
                part_type = random.choice(part_types)
                step_choices = [step for step in steps if step.part_model == part_type]
                assigned_emp = random.choice(users + [None])  # Allow unassigned parts

                part = Part(
                    name=f"{part_type.name} Part",
                    part_type=part_type,
                    step=random.choice(step_choices) if step_choices else None,
                    is_complete=random.choice([True, False]),
                    assigned_emp=assigned_emp,
                    customer=order.customer,
                    order=order,
                    estimated_completion=date.today() + timedelta(days=random.randint(1, 15))
                )
                parts.append(part)

        Part.objects.bulk_create(parts)
        self.stdout.write(self.style.SUCCESS(f"✅ Created {len(parts)} parts"))

        # Create Order Items
        order_items = [
            OrderItem(order=random.choice(orders), part=part)
            for part in parts
        ]
        OrderItem.objects.bulk_create(order_items)
        self.stdout.write(self.style.SUCCESS(f"✅ Created {len(order_items)} order items"))

        # Create PartDocs
        part_docs = list(PartDoc.objects.bulk_create([
            PartDoc(
                is_image=random.choice([True, False]),
                part_step=random.randint(1, 3),
                file_name=f"doc_{i}.pdf",
                file="parts_docs/dummy.pdf",
                uploader=random.choice(users + [None]),  # Allow null uploader
                part_type=random.choice(part_types)
            ) for i in range(5)
        ]))
        self.stdout.write(self.style.SUCCESS(f"✅ Created {len(part_docs)} part docs"))

        self.stdout.write(self.style.SUCCESS("🎉 Test data successfully populated!"))
