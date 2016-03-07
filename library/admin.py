from django.contrib import admin
from library.models import Lendable
# Register your models here.


class LendableAdmin(admin.ModelAdmin):
    list_display = ('pk', '__str__')


admin.site.register(Lendable, LendableAdmin)
