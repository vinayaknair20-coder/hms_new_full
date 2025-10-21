from django.contrib import admin
from .models import User, Specialization, Staff, Doctor

admin.site.register(User)
admin.site.register(Specialization)
admin.site.register(Staff)
admin.site.register(Doctor)
