from dataclasses import fields

from ..Serializer.S_GRNs import O_BatchWiseLiveStockSerializer
from ..models import *
from rest_framework import serializers
from ..Serializer.S_Companies import *
from ..Serializer.S_Parties import *
from ..Serializer.S_Items import *


class ProductionMaterialIssueSerializer(serializers.ModelSerializer):
    class Meta:
        model =TC_ProductionMaterialIssue
        fields=['MaterialIssue']

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model=M_Items
        fields=['id','Name']

class H_ProductionSerializerforGET(serializers.ModelSerializer):
    ProductionMaterialIssue=ProductionMaterialIssueSerializer(many=True)
    Item=ItemSerializer(read_only=True)
    Unit = ItemUnitsSerializerSecond(read_only=True)
    Company = C_CompanySerializer(read_only=True)
    Division = DivisionsSerializer(read_only=True)
    
    class Meta:
        model = T_Production
        fields = '__all__'

class H_ProductionSerializer(serializers.ModelSerializer):
    ProductionMaterialIssue=ProductionMaterialIssueSerializer(many=True)
    O_BatchWiseLiveStockItems = O_BatchWiseLiveStockSerializer(many=True)
    class Meta:
        model = T_Production
        fields = '__all__'

    def create(self, validated_data):
        ProductionMaterialIssues_data = validated_data.pop('ProductionMaterialIssue')
        O_BatchWiseLiveStockItems_data=validated_data.pop('O_BatchWiseLiveStockItems')
        
        ProductionID= T_Production.objects.create(**validated_data)
       
        for O_BatchWiseLiveStockItem_data in O_BatchWiseLiveStockItems_data :
            O_BatchWiseLiveStockdata=O_BatchWiseLiveStock.objects.create(Production=ProductionID,**O_BatchWiseLiveStockItem_data)  
          
        for ProductionMaterialIssue_data in ProductionMaterialIssues_data:
            Productionreff = TC_ProductionMaterialIssue.objects.create(Production=ProductionID, **ProductionMaterialIssue_data)
            
        return ProductionID



class ProductionMaterialIssueSerializer(serializers.ModelSerializer):
    class Meta:
        model =TC_ProductionMaterialIssue
        fields='__all__'

class M_MaterialissueItemsserializer(serializers.ModelSerializer):
    class Meta:
        model=M_Items
        fields=['id','Name']

class H_ProductionSerializer2(serializers.ModelSerializer):
    Item=M_MaterialissueItemsserializer(read_only=True)
    class Meta:
        model = T_MaterialIssue
        fields = '__all__'

class UnitSerializerSecond(serializers.ModelSerializer):
    class Meta:
        model = M_Units
        fields = ['id','Name']
        
class ItemUnitsSerializerSecond(serializers.ModelSerializer):
    UnitID = UnitSerializerSecond(read_only=True)
    class Meta:
        model = MC_ItemUnits
        fields = ['id','UnitID', 'BaseUnitQuantity','IsDeleted','IsBase','PODefaultUnit','SODefaultUnit']

class MaterialIssueSerializer(serializers.ModelSerializer):
    Item=M_MaterialissueItemsserializer(read_only=True)
    Unit = ItemUnitsSerializerSecond(read_only=True)
    class Meta:
        model = T_MaterialIssue
        fields = '__all__'
        fields = ['id','NumberOfLot','LotQuantity','Item','Unit']
    