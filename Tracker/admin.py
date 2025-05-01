from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# Register your models here.


from .models import Parts, PartDocs, PartTypes, Deals, Steps, User

admin.site.register(Parts)
admin.site.register(PartDocs)
admin.site.register(PartTypes)
admin.site.register(Deals)
admin.site.register(Steps)
admin.site.register(User, UserAdmin)
