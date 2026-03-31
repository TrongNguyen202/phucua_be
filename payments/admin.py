from django.contrib import admin
from .models import Payment, SePayTransaction


class SePayTransactionInline(admin.TabularInline):
    model         = SePayTransaction
    extra         = 0
    fields        = ["sepay_id", "gateway", "transfer_amount", "code", "is_matched", "created_at"]
    readonly_fields = fields

    def is_matched(self, obj):
        return obj.payment is not None
    is_matched.boolean = True
    is_matched.short_description = "Khớp?"


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display    = ["id", "order", "method", "status", "amount", "payment_code", "created_at"]
    list_filter     = ["method", "status"]
    search_fields   = ["payment_code", "order__id"]
    readonly_fields = ["payment_code", "created_at", "updated_at"]
    inlines         = [SePayTransactionInline]


@admin.register(SePayTransaction)
class SePayTransactionAdmin(admin.ModelAdmin):
    list_display  = ["sepay_id", "gateway", "transfer_amount", "code", "transfer_type", "transaction_date"]
    list_filter   = ["gateway", "transfer_type"]
    search_fields = ["sepay_id", "code", "content", "reference_code"]
    readonly_fields = [
        "sepay_id", "gateway", "transaction_date", "account_number",
        "sub_account", "transfer_type", "transfer_amount", "accumulated",
        "code", "content", "reference_code", "description", "raw_payload"
    ]