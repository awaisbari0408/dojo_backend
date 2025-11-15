from django.contrib import admin          # Imports Django’s built-in admin interface
from .models import User, DojoClass, Enrollment, Payment   # Imports all your models from models.py

# Registers each model so they appear in the Django admin dashboard
admin.site.register(User)
admin.site.register(DojoClass)
admin.site.register(Enrollment)
admin.site.register(Payment)
