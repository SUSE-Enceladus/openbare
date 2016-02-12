from django.contrib import admin
from library.models import Lendable
# Register your models here.


class LendableAdmin(admin.ModelAdmin):
    pass


admin.site.register(Lendable, LendableAdmin)
