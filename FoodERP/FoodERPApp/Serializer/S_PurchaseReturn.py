from ..Serializer.S_Invoices import Mc_ItemUnitSerializerThird
from ..models import *
from rest_framework import serializers
from ..Serializer.S_BankMaster import *
from ..Serializer.S_GeneralMaster import  *
from ..Serializer.S_Parties import  *
from ..Serializer.S_Items import *
from ..Serializer.S_Invoices import *

# Return Save Serializers

# UpdateO_BatchWiseLiveStockReturnSerializer  # Sales Returnconsoldated Stock Minus When Send to Supplier AND Self Purchase Return 
class UpdateO_BatchWiseLiveStockReturnSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField() 
    class Meta:
        model = O_BatchWiseLiveStock
        fields = ['id','Item','Quantity','Unit','BaseUnitQuantity','PurchaseReturn']


class O_BatchWiseLiveStockReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = O_BatchWiseLiveStock
        fields = ['Item','Quantity','Unit','OriginalBaseUnitQuantity','BaseUnitQuantity','Party','IsDamagePieces','CreatedBy']
    
class O_LiveBatchesReturnSerializer(serializers.ModelSerializer):
    
    O_BatchWiseLiveStockList = O_BatchWiseLiveStockReturnSerializer(many=True)
    UpdateO_BatchWiseLiveStockList = UpdateO_BatchWiseLiveStockReturnSerializer(many=True)
    class Meta:
        model = O_LiveBatches
        fields = ['MRP','MRPValue','GST','GSTPercentage','Rate','BatchDate', 'BatchCode','SystemBatchDate','SystemBatchCode','ItemExpiryDate','OriginalBatchBaseUnitQuantity','O_BatchWiseLiveStockList','UpdateO_BatchWiseLiveStockList']
    

class PurchaseReturnItemImageSerializer(serializers.ModelSerializer):
    class Meta :
        model= TC_PurchaseReturnItemImages
        fields = ['Item_pic']

class PurchaseReturnItemsSerializer(serializers.ModelSerializer):
    ReturnItemImages = PurchaseReturnItemImageSerializer(many=True)
    
    class Meta :
        model= TC_PurchaseReturnItems
        fields = fields = ['BatchCode', 'Quantity', 'BaseUnitQuantity', 'MRP', 'Rate', 'BasicAmount', 'TaxType', 'GST', 'GSTAmount', 'Amount','CGST', 'SGST', 'IGST', 'CGSTPercentage', 'SGSTPercentage', 'IGSTPercentage', 'CreatedOn', 'Item', 'Unit', 'BatchDate','ReturnItemImages','MRPValue','GSTPercentage','ItemReason','Comment','ApprovedQuantity','SubReturn','BatchID']   
        
class PurchaseReturnReferences(serializers.ModelSerializer):
    class Meta :
        model = TC_PurchaseReturnReferences
        fields =["SubReturn"]


class PurchaseReturnSerializer(serializers.ModelSerializer):
    ReturnItems = PurchaseReturnItemsSerializer(many=True)
    O_LiveBatchesList=O_LiveBatchesReturnSerializer(many=True)
    PurchaseReturnReferences=PurchaseReturnReferences(many=True)
    
    class Meta :
        model= T_PurchaseReturn
        fields = ['ReturnDate', 'ReturnNo', 'FullReturnNumber', 'GrandTotal', 'RoundOffAmount','ReturnReason', 'CreatedBy', 'UpdatedBy', 'Customer', 'Party','IsApproved', 'Comment', 'ReturnItems','O_LiveBatchesList','PurchaseReturnReferences','Mode']
        
        
    def create(self, validated_data):
        Mode = validated_data.get('Mode')
        ReturnItems_data = validated_data.pop('ReturnItems')
        O_LiveBatchesLists_data=validated_data.pop('O_LiveBatchesList')
        PurchaseReturnReferences_data=validated_data.pop('PurchaseReturnReferences')
        PurchaseReturnID = T_PurchaseReturn.objects.create(**validated_data)
        
        for ReturnItem_data in ReturnItems_data:
            ReturnItemImages_data = ReturnItem_data.pop('ReturnItemImages')
            ReturnItemID =TC_PurchaseReturnItems.objects.create(PurchaseReturn=PurchaseReturnID, **ReturnItem_data)
            
            for ReturnItemImage_data in ReturnItemImages_data:
                ItemImages =TC_PurchaseReturnItemImages.objects.create(PurchaseReturnItem=ReturnItemID, **ReturnItemImage_data)
        
        if (Mode == 1 or Mode ==3): # For Sales Return and Consolidated Sales Return update BatchID Null       
            update = TC_PurchaseReturnItems.objects.filter(PurchaseReturn =PurchaseReturnID).update(BatchID = None)  
        
        if PurchaseReturnReferences_data : 
            for PurchaseReturnReference_data in PurchaseReturnReferences_data:
                ReturnReference=TC_PurchaseReturnReferences.objects.create(PurchaseReturn=PurchaseReturnID, **PurchaseReturnReference_data)
        
        
        if Mode == 1:  # Sales Return Save
            for O_LiveBatchesList_data in O_LiveBatchesLists_data :
                O_BatchWiseLiveStockLists=O_LiveBatchesList_data.pop('O_BatchWiseLiveStockList')
                UpdateO_BatchWiseLiveStockLists=O_LiveBatchesList_data.pop('UpdateO_BatchWiseLiveStockList')
                BatchID=O_LiveBatches.objects.create(**O_LiveBatchesList_data)
                for O_BatchWiseLiveStockList in O_BatchWiseLiveStockLists:
                    O_BatchWiseLiveStockdata=O_BatchWiseLiveStock.objects.create(PurchaseReturn=PurchaseReturnID,LiveBatche=BatchID,**O_BatchWiseLiveStockList)  
            
        if Mode == 2: # Purchase Return Save
            for O_LiveBatchesList_data in O_LiveBatchesLists_data :
                UpdateO_BatchWiseLiveStockLists=O_LiveBatchesList_data.pop('UpdateO_BatchWiseLiveStockList')
                for UpdateO_BatchWiseLiveStockList in UpdateO_BatchWiseLiveStockLists:
                    OBatchQuantity=O_BatchWiseLiveStock.objects.filter(id=UpdateO_BatchWiseLiveStockList['id'],Item=UpdateO_BatchWiseLiveStockList['Item']).values('BaseUnitQuantity')
                    if(OBatchQuantity[0]['BaseUnitQuantity'] >= UpdateO_BatchWiseLiveStockList['BaseUnitQuantity']):
                        OBatchWiseLiveStock=O_BatchWiseLiveStock.objects.filter(id=UpdateO_BatchWiseLiveStockList['id'],Item=UpdateO_BatchWiseLiveStockList['Item'],PurchaseReturn=UpdateO_BatchWiseLiveStockList['PurchaseReturn']).update(BaseUnitQuantity =  OBatchQuantity[0]['BaseUnitQuantity'] - UpdateO_BatchWiseLiveStockList['BaseUnitQuantity'])     
        
        
        if Mode == 3: # Sales Returnconsoldated Stock Minus When Send to Supplier
            for O_LiveBatchesList_data in O_LiveBatchesLists_data :
                O_BatchWiseLiveStockLists=O_LiveBatchesList_data.pop('O_BatchWiseLiveStockList')
                UpdateO_BatchWiseLiveStockLists=O_LiveBatchesList_data.pop('UpdateO_BatchWiseLiveStockList')
                for UpdateO_BatchWiseLiveStockList in UpdateO_BatchWiseLiveStockLists:
                    OBatchQuantity=O_BatchWiseLiveStock.objects.filter(Item=UpdateO_BatchWiseLiveStockList['Item'],PurchaseReturn=UpdateO_BatchWiseLiveStockList['PurchaseReturn']).values('BaseUnitQuantity')
                    if(OBatchQuantity[0]['BaseUnitQuantity'] >= UpdateO_BatchWiseLiveStockList['BaseUnitQuantity']):
                        OBatchWiseLiveStock=O_BatchWiseLiveStock.objects.filter(Item=UpdateO_BatchWiseLiveStockList['Item'],PurchaseReturn=UpdateO_BatchWiseLiveStockList['PurchaseReturn']).update(BaseUnitQuantity =  OBatchQuantity[0]['BaseUnitQuantity'] - UpdateO_BatchWiseLiveStockList['BaseUnitQuantity'])     
                            
        return PurchaseReturnID      

############################ Purchase Return Stock details Serializer ##################################### 

class StockItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = M_Items
        fields = ['id','Name']        
class StockQtyserializerForPurchaseReturn(serializers.ModelSerializer):
    LiveBatche=LiveBatchSerializer(read_only=True)
    Unit = Mc_ItemUnitSerializerThird()
    Item = StockItemSerializer()
    class Meta:
        model = O_BatchWiseLiveStock
        fields = ['id','Item','Quantity','BaseUnitQuantity','Party','LiveBatche','Unit'] 

        
############################## Return List serializer########################################################################

class PurchaseReturnSerializerSecond(serializers.ModelSerializer):
    ReturnReason = GeneralMasterserializer(read_only=True)
    Party = PartiesSerializer(read_only=True)
    Customer = PartiesSerializer(read_only=True)
    ReturnItems = PurchaseReturnItemsSerializer(read_only=True,many=True)
    class Meta :
        model= T_PurchaseReturn
        fields = '__all__'       
     
    def to_representation(self, instance):
        # get representation from ModelSerializer
        ret = super(PurchaseReturnSerializerSecond, self).to_representation(instance)
        # if parent is None, overwrite
        if not ret.get("ReturnReason", None):
            ret["ReturnReason"] = {"id": None, "Name": None}
              
        return ret    
    
class ItemsReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model= M_GeneralMaster
        fields= ['id','Name']

class M_ItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model= M_Items
        fields= ['id','Name']

class PurchaseReturnItemsSerializer(serializers.ModelSerializer):
    Item = M_ItemsSerializer()
    ItemReason = ItemsReasonSerializer()
    Unit=Mc_ItemUnitSerializerThird()
    class Meta :
        model= TC_PurchaseReturnItems
        fields = '__all__'

    
class PurchaseReturnSerializerThird(serializers.ModelSerializer):
    ReturnItems = PurchaseReturnItemsSerializer(read_only=True,many=True)
    class Meta :
        model= T_PurchaseReturn
        fields = '__all__'


class PurchaseReturnItemsSerializer2(serializers.ModelSerializer):
    Item=M_ItemsSerializer(read_only=True)
    ItemReason = GeneralMasterserializer(read_only=True)
    Unit = Mc_ItemUnitSerializerThird(read_only=True)
    class Meta :
        model= TC_PurchaseReturnItems
        fields = '__all__'
        

###################### Purchase Return Print Serializers ########################################## 


class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = M_States
        fields = '__all__'
        
class MC_PartyAdressSerializer(serializers.ModelSerializer):
    Address = serializers.CharField() 
    class Meta:
        model = MC_PartyAddress
        fields = '__all__'

class PartiesSerializerPrintSecond(serializers.ModelSerializer):
    PartyAddress=MC_PartyAdressSerializer(many=True)
    State = StateSerializer(read_only=True)
    class Meta:
        model = M_Parties
        fields = ['id','Name','GSTIN','PAN','Email','PartyAddress','State','MobileNo'] 


class PurchaseReturnPrintItemsSerializer(serializers.ModelSerializer):
    MRP = M_MRPsSerializer(read_only=True)
    GST = M_GstHsnCodeSerializer(read_only=True)
    # Margin = M_MarginsSerializer(read_only=True)
    Item = M_ItemsSerializer01(read_only=True)
    ItemReason = GeneralMasterserializer(read_only=True)
    Unit = Mc_ItemUnitSerializerThird(read_only=True)
    class Meta :
        model= TC_PurchaseReturnItems
        fields = '__all__'        
        
class PurchaseReturnPrintSerilaizer(serializers.ModelSerializer):
    Customer = PartiesSerializerPrintSecond(read_only=True)
    Party = PartiesSerializerPrintSecond(read_only=True)
    ReturnItems = PurchaseReturnPrintItemsSerializer(read_only=True,many=True)
    class Meta :
        model= T_PurchaseReturn
        fields = '__all__'
        
        
        
class SalesReturnApproveQtySerializer(serializers.ModelSerializer):
    
    O_BatchWiseLiveStockList = O_BatchWiseLiveStockReturnSerializer(many=True)
    class Meta:
        model = O_LiveBatches
        fields = ['MRP','MRPValue','GST','GSTPercentage','Rate','BatchDate', 'BatchCode','SystemBatchDate','SystemBatchCode','ItemExpiryDate','OriginalBatchBaseUnitQuantity','O_BatchWiseLiveStockList','UpdateO_BatchWiseLiveStockList']                    

    
    def create(self, validated_data):
        O_LiveBatchesLists_data=validated_data.pop('O_LiveBatchesList')
 
        for O_LiveBatchesList_data in O_LiveBatchesLists_data :
            O_BatchWiseLiveStockLists=O_LiveBatchesList_data.pop('O_BatchWiseLiveStockList')
            BatchID=O_LiveBatches.objects.create(**O_LiveBatchesList_data)
            for O_BatchWiseLiveStockList in O_BatchWiseLiveStockLists:
                O_BatchWiseLiveStockdata=O_BatchWiseLiveStock.objects.create(LiveBatche=BatchID,**O_BatchWiseLiveStockList)  
