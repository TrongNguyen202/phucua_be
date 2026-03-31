from rest_framework import serializers
from .models import Payment, SePayTransaction


class SePayTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model  = SePayTransaction
        fields = [
            "id", "sepay_id", "gateway", "transaction_date",
            "transfer_type", "transfer_amount", "code", "content", "created_at"
        ]
        read_only_fields = fields


class PaymentSerializer(serializers.ModelSerializer):

    sepay_transactions = SePayTransactionSerializer(many=True, read_only=True)

    class Meta:
        model  = Payment
        fields = [
            "id", "order", "method", "status", "amount",
            "payment_code", "sepay_transactions",
            "created_at", "updated_at"
        ]
        read_only_fields = ["id", "status", "payment_code", "created_at", "updated_at"]


class CreatePaymentSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    method   = serializers.ChoiceField(choices=Payment.Method.choices)


# Webhook payload từ SePay
class SePayWebhookSerializer(serializers.Serializer):
    id              = serializers.IntegerField()
    gateway         = serializers.CharField()
    transactionDate = serializers.DateTimeField(input_formats=["%Y-%m-%d %H:%M:%S"])
    accountNumber   = serializers.CharField()
    subAccount      = serializers.CharField(allow_null=True, required=False)
    transferType    = serializers.CharField()
    transferAmount  = serializers.DecimalField(max_digits=14, decimal_places=2)
    accumulated     = serializers.DecimalField(max_digits=14, decimal_places=2)
    code            = serializers.CharField(allow_null=True, required=False)
    content         = serializers.CharField(allow_blank=True, default="")
    referenceCode   = serializers.CharField(allow_blank=True, default="")
    description     = serializers.CharField(allow_blank=True, default="")