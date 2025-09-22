"""Django admin setup (no model registrations for MongoEngine)."""

from django.contrib import admin

admin.site.site_header = "BudgetFlow Admin"
admin.site.site_title = "BudgetFlow Admin"
admin.site.index_title = "Administration"

