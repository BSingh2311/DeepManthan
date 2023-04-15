from ..models import *
from rest_framework import serializers
from ..Serializer.S_BankMaster import *
from ..Serializer.S_GeneralMaster import  *
from ..Serializer.S_Parties import  *

class ReceiptInvoiceserializer(serializers.Serializer):
   
    Receipt_id=serializers.IntegerField()
    Customer_id=serializers.IntegerField()
    Invoice_ID=serializers.IntegerField()
    InvoiceDate = serializers.DateField()
    CustomerName=serializers.CharField(max_length=100)
    FullInvoiceNumber=serializers.CharField(max_length=100)
    GrandTotal=serializers.DecimalField(max_digits=10, decimal_places=2)  
    PaidAmount=serializers.DecimalField(max_digits=10, decimal_places=2)  
    BalAmt=serializers.DecimalField(max_digits=10, decimal_places=2)  
    

class PaymentReceiptSerializer(serializers.ModelSerializer):
    class Meta :
        model= TC_PaymentReceipt
        fields = ['Payment']

class ReceiptInvoiceSerializer(serializers.ModelSerializer):
    class Meta :
        model= TC_ReceiptInvoices
        fields = ['Invoice','GrandTotal','PaidAmount','AdvanceAmtAdjusted']

class ReceiptSerializer(serializers.ModelSerializer):
    ReceiptInvoices = ReceiptInvoiceSerializer(many=True)
    PaymentReceipt=PaymentReceiptSerializer(many=True)
    class Meta :
        model= T_Receipts
        fields = ['ReceiptDate', 'ReceiptNo', 'Description', 'AmountPaid', 'ChequeDate','BalanceAmount', 'OpeningBalanceAdjusted', 'DocumentNo' , 'Bank', 'Customer', 'DepositorBank', 'Party', 'CreatedBy', 'UpdatedBy', 'FullReceiptNumber', 'ReceiptMode', 'ReceiptType','ReceiptInvoices','PaymentReceipt']
        
    def create(self, validated_data):
        ReceiptInvoices_data = validated_data.pop('ReceiptInvoices')
        PaymentReceipts_data = validated_data.pop('PaymentReceipt')
        Receipts = T_Receipts.objects.create(**validated_data)
        
        for ReceiptInvoice_data in ReceiptInvoices_data:
           TC_ReceiptInvoices.objects.create(Receipt=Receipts, **ReceiptInvoice_data)
        
        for PaymentReceipt_data in PaymentReceipts_data:
            TC_PaymentReceipt.objects.create(Receipt=Receipts, **PaymentReceipt_data)    

        return Receipts    
        
        
class ReceiptSerializerSecond(serializers.ModelSerializer):
    Customer = PartiesSerializer(read_only=True)
    Party = PartiesSerializer(read_only=True)
    ReceiptMode = GeneralMasterserializer(read_only=True)
    ReceiptType = GeneralMasterserializer(read_only=True)
    Bank = BankSerializer(read_only=True)
    DepositorBank = BankSerializer(read_only=True)
    ReceiptInvoices = ReceiptInvoiceSerializer(many=True)
    PaymentReceipt=PaymentReceiptSerializer()
    
    class Meta:
        model = T_Receipts
        fields = '__all__'
                
    def to_representation(self, instance):
        # get representation from ModelSerializer
        ret = super(ReceiptSerializerSecond, self).to_representation(instance)
        # if parent is None, overwrite
        if not ret.get("Bank", None):
            ret["Bank"] = {"id": None, "Name": None}
        
        if not ret.get("DepositorBank", None):
            ret["DepositorBank"] = {"id": None, "Name": None}
        
        if not ret.get("ReceiptMode", None):
            ret["ReceiptMode"] = {"id": None, "Name": None}  
        
        if not ret.get("ReceiptType", None):
            ret["ReceiptType"] = {"id": None, "Name": None}      
                  
        return ret            