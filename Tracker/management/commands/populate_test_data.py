from django.core.management.base import BaseCommand
from django.utils import timezone
from Tracker.models import Companies, User, PartType, Step, Deal, Part, DealItem, Equipment, EquipmentUsed
import random

class Command(BaseCommand):
    help = "Populate the database with sample data"

    def handle(self, *args, **kwargs):
        # Create Companies
        company1 = Companies.objects.create(name="TechCorp", description="A leading tech manufacturer.")
        company2 = Companies.objects.create(name="MechaWorks", description="Experts in mechanical parts.")

        # Create Users
        user1 = User.objects.create(username="john_doe", email="john@example.com", parent_company=company1)
        user2 = User.objects.create(username="jane_smith", email="jane@example.com", parent_company=company2)

        # Create Part Types
        part_type1 = PartType.objects.create(name="Gizmo", num_steps=3)
        part_type2 = PartType.objects.create(name="Widget", num_steps=4)

        # Create Steps
        steps = []
        for i in range(1, 4):
            step = Step.objects.create(step=i, description=f"Step {i} for Gizmo", part_model=part_type1, completion_time=timezone.now().time())
            steps.append(step)

        for i in range(1, 5):
            step = Step.objects.create(step=i, description=f"Step {i} for Widget", part_model=part_type2, completion_time=timezone.now().time())
            steps.append(step)

        # Create Deals
        deal1 = Deal.objects.create(name="Deal A", customer=user1, company=company1, estimated_completion=timezone.now().date(), status=Deal.Status.PENDING)
        deal2 = Deal.objects.create(name="Deal B", customer=user2, company=company2, estimated_completion=timezone.now().date(), status=Deal.Status.IN_PROGRESS)

        # Create Parts
        part1 = Part.objects.create(name="Gizmo Part A", part_type=part_type1, step=steps[0], assigned_emp=user1, customer=user1, deal=deal1, estimated_completion=timezone.now().date(), status=Part.Status.PENDING)
        part2 = Part.objects.create(name="Widget Part B", part_type=part_type2, step=steps[2], assigned_emp=user2, customer=user2, deal=deal2, estimated_completion=timezone.now().date(), status=Part.Status.IN_PROGRESS)

        # Create Deal Items
        DealItem.objects.create(deal=deal1, part=part1)
        DealItem.objects.create(deal=deal2, part=part2)

        # Create Equipment
        equipment1 = Equipment.objects.create(equipmentType=Equipment.EquipmentType.ASSEMBLER)
        equipment2 = Equipment.objects.create(equipmentType=Equipment.EquipmentType.Unassigned)

        # Assign Equipment to Steps
        EquipmentUsed.objects.create(equipment=equipment1, step=steps[0], part=part1)
        EquipmentUsed.objects.create(equipment=equipment2, step=steps[2], part=part2)

        self.stdout.write(self.style.SUCCESS("Database successfully populated with sample data!"))