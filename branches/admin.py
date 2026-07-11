from django.contrib import admin

from branches.models import Branch, BranchHour, Category

admin.site.register(Branch)
admin.site.register(BranchHour)
admin.site.register(Category)
