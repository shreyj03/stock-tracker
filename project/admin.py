from django.contrib import admin

# Register your models here.
# project/admin.py
# Shrey Jain, shreyj@bu.edu 4/19/2026
# Registers project models with the Django admin interface.

from .models import Profile, Stock, Watchlist, Transaction

admin.site.register(Profile)
admin.site.register(Stock)
admin.site.register(Watchlist)
admin.site.register(Transaction)
