from django.contrib import admin

from users.models import AccountVerification, Address, CashbackHistory, User

admin.site.register(User)
admin.site.register(AccountVerification)
admin.site.register(CashbackHistory)
admin.site.register(Address)
