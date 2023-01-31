from django.contrib import admin
from .models import CarModel, CarMake


class CarModelInline(admin.StackedInline):
    model = CarModel
    extra = 1


class CarMakeAdmin(admin.ModelAdmin):
    inlines = [CarModelInline]


admin.site.register(CarMake, CarMakeAdmin)
admin.site.register(CarModel)
