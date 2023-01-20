from dataclasses import fields
import json
from ..models import *
from rest_framework import serializers
from ..Serializer.S_Items import *

class PartiesSerializerSecond(serializers.ModelSerializer):
    class Meta:
        model = M_Parties
        fields = ['id','Name']

class UnitSerializerThird(serializers.ModelSerializer):
    class Meta:
        model = M_Units
        fields = ['id','Name']
        
class Mc_ItemUnitSerializerThird(serializers.ModelSerializer):
    UnitID = UnitSerializerThird(read_only=True)
    class Meta:
        model = MC_ItemUnits
        fields = ['id','UnitID','BaseUnitQuantity','IsDeleted','IsBase','PODefaultUnit','SODefaultUnit'] 
class LiveBatchSerializer(serializers.ModelSerializer):
    class Meta:
        model =O_LiveBatches
        fields='__all__'

class StockQtyserializerForIBChallan(serializers.ModelSerializer):
    LiveBatche=LiveBatchSerializer()
    Unit = Mc_ItemUnitSerializerThird()
    Item =  ItemSerializerSecond()
    class Meta:
        model = O_BatchWiseLiveStock
        fields = ['id','Item','Quantity','BaseUnitQuantity','Party','LiveBatche','Unit']  

class OrderserializerforIBChallan(serializers.ModelSerializer):
    class Meta:
        model = T_Orders
        fields = '__all__'



class IBChallansReferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = TC_InterbranchChallanReferences
        fields = ['Demand']
        
class IBChallanItemsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = TC_InterbranchChallanItems
        fields = ['BatchCode', 'Quantity', 'BaseUnitQuantity', 'MRP', 'Rate', 'BasicAmount', 'TaxType', 'GSTPercentage', 'GSTAmount', 'Amount', 'DiscountType', 'Discount', 'DiscountAmount', 'CGST', 'SGST', 'IGST', 'CGSTPercentage', 'SGSTPercentage', 'IGSTPercentage', 'CreatedOn', 'Item', 'Unit', 'BatchDate','LiveBatch']   

class obatchwiseStockSerializer(serializers.ModelSerializer):
    class Meta:
        model=O_BatchWiseLiveStock
        fields=['Quantity','BaseUnitQuantity','Item']
        
class IBChallanSerializer(serializers.ModelSerializer):
    IBChallanItems = IBChallanItemsSerializer(many=True)
    IBChallansReferences = IBChallansReferencesSerializer(many=True) 
    obatchwiseStock=obatchwiseStockSerializer(many=True)
    class Meta:
        model = T_InterbranchChallan
        fields = ['IBChallanDate', 'IBChallanNumber', 'FullIBChallanNumber', 'CustomerGSTTin', 'GrandTotal', 'RoundOffAmount', 'CreatedBy', 'UpdatedBy', 'Customer', 'Party', 'IBChallanItems', 'IBChallansReferences', 'obatchwiseStock']

    def create(self, validated_data):
        IBChallanItems_data = validated_data.pop('IBChallanItems')
        IBChallansReferences_data = validated_data.pop('IBChallansReferences')
        O_BatchWiseLiveStockItems_data = validated_data.pop('obatchwiseStock')
        IBChallanID = T_InterbranchChallan.objects.create(**validated_data)
        
        for IBChallanItem_data in IBChallanItems_data:
            IBChallanItemID =TC_InterbranchChallanItems.objects.create(IBChallan=IBChallanID, **IBChallanItem_data)
            
        for O_BatchWiseLiveStockItem_data in O_BatchWiseLiveStockItems_data:
            
                OBatchQuantity=O_BatchWiseLiveStock.objects.filter(id=O_BatchWiseLiveStockItem_data['Quantity']).values('BaseUnitQuantity')
                
                if(OBatchQuantity[0]['BaseUnitQuantity'] >= O_BatchWiseLiveStockItem_data['BaseUnitQuantity']):
                    OBatchWiseLiveStock=O_BatchWiseLiveStock.objects.filter(id=O_BatchWiseLiveStockItem_data['Quantity']).update(BaseUnitQuantity =  OBatchQuantity[0]['BaseUnitQuantity'] - O_BatchWiseLiveStockItem_data['BaseUnitQuantity'])
                else:
                    
                    raise serializers.ValidationError("Not In Stock ")    
          
        for IBChallansReference_data in IBChallansReferences_data:
            IBChallansReferences = TC_InterbranchChallanReferences.objects.create(IBChallan=IBChallanID, **IBChallansReference_data)       
        
        return IBChallanID   
    
    
    
class IBChallanSerializerSecond(serializers.ModelSerializer):
    Customer = PartiesSerializerSecond(read_only=True)
    Party = PartiesSerializerSecond(read_only=True)
 
    class Meta:
        model = T_InterbranchChallan
        fields = '__all__'    

class IBChallanSerializerForDelete(serializers.ModelSerializer):
    IBChallanItems = IBChallanItemsSerializer(many=True)
 
    class Meta:
        model = T_InterbranchChallan
        fields = '__all__'               