from dataclasses import fields
import json
from ..models import *
from rest_framework import serializers


class LiveBatchSerializer(serializers.ModelSerializer):
    class Meta:
        model =O_LiveBatches
        fields='__all__'

class StockQtyserializerForInvoice(serializers.ModelSerializer):
    LiveBatche=LiveBatchSerializer()
    class Meta:
        model = O_BatchWiseLiveStock
        fields = ['id','Item','Quantity','BaseUnitQuantity','Party','LiveBatche']  

class OrderserializerforInvoice(serializers.ModelSerializer):
    class Meta:
        model = T_Orders
        fields = '__all__'



# class T_InvoiceSerializerGETList(serializers.Serializer):
#     id=serializers.IntegerField()
#     Customer_id = serializers.IntegerField()
#     CustomerName=serializers.CharField(max_length=500)
#     Party_id =serializers.IntegerField()
#     PartyName=serializers.CharField(max_length=500)
#     InvoiceDate = serializers.DateField()
#     InvoiceNumber  =  serializers.IntegerField()
#     FullInvoiceNumber =  serializers.CharField(max_length=500)
#     CustomerGSTTin = serializers.CharField(max_length=500)
#     GrandTotal =  serializers.DecimalField(max_digits = 15,decimal_places=2)
#     RoundOffAmount = serializers.DecimalField(max_digits = 5,decimal_places=2)
#     CreatedBy  =  serializers.IntegerField()
#     CreatedOn =  serializers.DateTimeField()
#     UpdatedBy = serializers.IntegerField()
#     UpdatedOn = serializers.DateTimeField()
#     Order_id = serializers.IntegerField()
    
    


class InvoicesReferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = TC_InvoicesReferences
        fields = ['Order']
        
class InvoiceItemsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = TC_InvoiceItems
        fields = ['BatchCode', 'Quantity', 'BaseUnitQuantity', 'MRP', 'Rate', 'BasicAmount', 'TaxType', 'GSTPercentage', 'GSTAmount', 'Amount', 'DiscountType', 'Discount', 'DiscountAmount', 'CGST', 'SGST', 'IGST', 'CGSTPercentage', 'SGSTPercentage', 'IGSTPercentage', 'CreatedOn', 'Item', 'Unit', 'BatchDate']   

class obatchwiseStockSerializer(serializers.ModelSerializer):
    class Meta:
        model=O_BatchWiseLiveStock
        fields=['Quantity','BaseUnitQuantity','Item']
        
class InvoiceSerializer(serializers.ModelSerializer):
    InvoiceItems = InvoiceItemsSerializer(many=True)
    InvoicesReferences = InvoicesReferencesSerializer(many=True) 
    obatchwiseStock=obatchwiseStockSerializer(many=True)
    class Meta:
        model = T_Invoices
        fields = ['InvoiceDate', 'InvoiceNumber', 'FullInvoiceNumber', 'CustomerGSTTin', 'GrandTotal', 'RoundOffAmount', 'CreatedBy', 'UpdatedBy', 'Customer', 'Party', 'InvoiceItems', 'InvoicesReferences', 'obatchwiseStock']

    def create(self, validated_data):
        InvoiceItems_data = validated_data.pop('InvoiceItems')
        InvoicesReferences_data = validated_data.pop('InvoicesReferences')
        O_BatchWiseLiveStockItems_data = validated_data.pop('obatchwiseStock')
        InvoiceID = T_Invoices.objects.create(**validated_data)
        
        for InvoiceItem_data in InvoiceItems_data:
            InvoiceItemID =TC_InvoiceItems.objects.create(Invoice=InvoiceID, **InvoiceItem_data)
            
        for O_BatchWiseLiveStockItem_data in O_BatchWiseLiveStockItems_data:
            
                OBatchQuantity=O_BatchWiseLiveStock.objects.filter(id=O_BatchWiseLiveStockItem_data['Quantity']).values('BaseUnitQuantity')
                
                if(OBatchQuantity[0]['BaseUnitQuantity'] >= O_BatchWiseLiveStockItem_data['BaseUnitQuantity']):
                    OBatchWiseLiveStock=O_BatchWiseLiveStock.objects.filter(id=O_BatchWiseLiveStockItem_data['Quantity']).update(BaseUnitQuantity =  OBatchQuantity[0]['BaseUnitQuantity'] - O_BatchWiseLiveStockItem_data['BaseUnitQuantity'])
                else:
                    
                    raise serializers.ValidationError("Not In Stock ")    
          
        for InvoicesReference_data in InvoicesReferences_data:
            InvoicesReferences = TC_InvoicesReferences.objects.create(Invoice=InvoiceID, **InvoicesReference_data)       
        
        return InvoiceID       