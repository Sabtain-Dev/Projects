from django.contrib import admin
from finance.models import Transaction, Goal
from import_export import resources
from import_export.admin import ImportMixin

class TransactionResource(resources.ModelResource):
    class Meta:
        model = Transaction
        fields = ('title', 'amount', 'transaction_type', 'date')

class TransactionAdmin(ImportMixin, admin.ModelAdmin):
    resource_class = TransactionResource
    list_display = ('title', 'amount', 'transaction_type', 'date')
    list_filter = ('transaction_type', 'date')
    search_fields = ('title',)

# Register your models here.
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Goal)