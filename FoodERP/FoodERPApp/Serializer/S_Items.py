from dataclasses import field
from ..models import *
from rest_framework import serializers


class M_ItemsSerializer01(serializers.ModelSerializer):
    class Meta:
        model = M_Items
        fields = '__all__'


class M_ItemsSerializer02(serializers.Serializer):
    id = serializers.IntegerField()
    Name = serializers.CharField(max_length=500)
    BaseUnitName = serializers.CharField(max_length=500)
    CompanyName = serializers.CharField(max_length=500)
    CategoryTypeName = serializers.CharField(max_length=500)
    CategoryName = serializers.CharField(max_length=500)
    SubCategoryName = serializers.CharField(max_length=500)
   

class MRPTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = M_MRPTypes
        fields = '__all__'


class ImageTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = M_ImageTypes
        fields = '__all__'


class ItemMarginSerializer(serializers.ModelSerializer):
    class Meta:
        model = MC_ItemMargin
        fields = ['PriceList', 'Margin']

class ItemMRPSerializer(serializers.ModelSerializer):
    class Meta:
        model = MC_ItemMRP
        fields = ['GSTPercentage','MRPType', 'MRP', 'HSNCode']
        
        
class ItemDivisionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MC_ItemDivisions
        fields = ['Division']          
        
class ItemImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = MC_ItemImages
        fields = ['ImageType', 'Item_pic']        
         
class ItemUnitsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MC_ItemUnits
        fields = ['UnitID', 'BaseUnitQuantity' ]
        
class ItemCategoryDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MC_ItemCategoryDetails
        fields = ['CategoryType', 'Category', 'SubCategory']


class ItemSerializer(serializers.ModelSerializer):
    
    ItemCategoryDetails = ItemCategoryDetailsSerializer(many=True)
    
    ItemUnitDetails = ItemUnitsSerializer(many=True)
    
    ItemImagesDetails = ItemImagesSerializer(many=True)
    
    ItemDivisionDetails = ItemDivisionsSerializer(many=True) 
    
    ItemMRPDetails = ItemMRPSerializer(many=True)

    ItemMarginDetails = ItemMarginSerializer(many=True)
    
   
    class Meta:
        model = M_Items
        fields = ['Name', 'ShortName', 'Sequence', 'Company', 'BaseUnitID', 'BarCode', 'isActive',
                  'CreatedBy', 'UpdatedBy','ItemCategoryDetails', 'ItemUnitDetails', 'ItemImagesDetails', 'ItemDivisionDetails', 'ItemMRPDetails', 'ItemMarginDetails' ]

    def create(self, validated_data):
        ItemCategorys_data = validated_data.pop('ItemCategoryDetails')
        ItemUnits_data = validated_data.pop('ItemUnitDetails')
        ItemImages_data = validated_data.pop('ItemImagesDetails')
        ItemDivisions_data = validated_data.pop('ItemDivisionDetails')
        ItemMRPs_data = validated_data.pop('ItemMRPDetails')
        ItemMargins_data = validated_data.pop('ItemMarginDetails')
        ItemID= M_Items.objects.create(**validated_data)
        
        for ItemCategory_data in ItemCategorys_data:
            ItemCategorys = MC_ItemCategoryDetails.objects.create(Item=ItemID, **ItemCategory_data)

        for ItemUnit_data in ItemUnits_data:
            ItemUnits = MC_ItemUnits.objects.create(Item=ItemID, **ItemUnit_data)
            
        for ItemImage_data in ItemImages_data:
            ItemImage = MC_ItemImages.objects.create(Item=ItemID, **ItemImage_data)
        
        for ItemDivision_data in ItemDivisions_data:
            ItemDivision = MC_ItemDivisions.objects.create(Item=ItemID, **ItemDivision_data)    
        
        for ItemMRP_data in ItemMRPs_data:
            ItemGstMrp = MC_ItemMRP.objects.create(Item=ItemID, **ItemMRP_data)
        
        for ItemMargin_data in ItemMargins_data:
            ItemMargin = MC_ItemMargin.objects.create(Item=ItemID, **ItemMargin_data)             

        return ItemID
