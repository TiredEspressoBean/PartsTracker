from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# Register your models here.


from .models import Part, PartDoc, PartType, Deal, Step, User

admin.site.register(Part)
admin.site.register(PartDoc)
admin.site.register(PartType)
admin.site.register(Deal)
admin.site.register(Step)
admin.site.register(User, UserAdmin)
