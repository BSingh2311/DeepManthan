from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from ..Views.V_TransactionNumberfun import GetMaxNumber, GetPrifix, SystemBatchCodeGeneration
from ..Serializer.S_CreditDebit import *
from ..Serializer.S_Items import *
from ..Serializer.S_GRNs import *
from django.db.models import Sum
from ..models import *
import datetime

class PurchaseReturnListView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request, id=0):
        try:
            with transaction.atomic():
                Returndata = JSONParser().parse(request)
                FromDate = Returndata['FromDate']
                ToDate = Returndata['ToDate']
                Customer = Returndata['CustomerID']
                Party = Returndata['PartyID']

                if(Customer == ''):
                    query = T_PurchaseReturn.objects.filter(ReturnDate__range=[FromDate, ToDate], Party=Party)
                else:
                    query = T_PurchaseReturn.objects.filter(ReturnDate__range=[FromDate, ToDate], Customer=Customer, Party=Party)
                if query:
                    Return_serializer = PurchaseReturnSerializerSecond(query, many=True).data
                    ReturnListData = list()
                    for a in Return_serializer:
                        ReturnListData.append({
                            "id": a['id'],
                            "ReturnDate": a['ReturnDate'],
                            "ReturnNo": a['ReturnNo'],
                            "FullReturnNumber": a['FullReturnNumber'],
                            "ReturnReasonID":a['ReturnReason']['id'],
                            "ReturnReasonName":a['ReturnReason']['Name'],
                            "CustomerID": a['Customer']['id'],
                            "Customer": a['Customer']['Name'],
                            "PartyID": a['Party']['id'],
                            "Party": a['Party']['Name'],
                            "GrandTotal": a['GrandTotal'],
                            "RoundOffAmount": a['RoundOffAmount'],
                            "CreatedOn": a['CreatedOn']
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': ReturnListData})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Record Not Found', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
    


class PurchaseReturnView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                PurchaseReturndata = JSONParser().parse(request)
                Party = PurchaseReturndata['Party']
                Date = PurchaseReturndata['ReturnDate']
                c = GetMaxNumber.GetPurchaseReturnNumber(Party,Date)
                PurchaseReturndata['ReturnNo'] = str(c)
                d = GetPrifix.GetPurchaseReturnPrifix(Party)
                PurchaseReturndata['FullReturnNumber'] = str(d)+""+str(c)
                
                item = ""
                query = T_PurchaseReturn.objects.filter(Party_id=Party).values('id')
                O_BatchWiseLiveStockList=list()
                O_LiveBatchesList=list()
              
                   
                    
                for a in PurchaseReturndata['ReturnItems']:
                    
                    if a['ReturnReason'] == 56:
                        
                        IsDamagePieces =False
                    else:
                        IsDamagePieces =True 
                    
                    
                    query1 = TC_PurchaseReturnItems.objects.filter(Item_id=a['Item'], BatchDate=date.today(), PurchaseReturn_id__in=query).values('id')
                    query2=MC_ItemShelfLife.objects.filter(Item_id=a['Item'],IsDeleted=0).values('Days')
                    if(item == ""):
                        item = a['Item']
                        b = query1.count()

                    elif(item == a['Item']):
                        item = 1
                        b = b+1
                    else:
                        item = a['Item']
                        b = 0
                        
                    BatchCode = SystemBatchCodeGeneration.GetGrnBatchCode(a['Item'],Party, b)
                    UnitwiseQuantityConversionobject=UnitwiseQuantityConversion(a['Item'],a['Quantity'],a['Unit'],0,0,0,0)
                    BaseUnitQuantity=UnitwiseQuantityConversionobject.GetBaseUnitQuantity()
                    
                    a['SystemBatchCode'] = BatchCode
                    a['SystemBatchDate'] = date.today()
                    a['BaseUnitQuantity'] = BaseUnitQuantity
                    
                    
                    O_BatchWiseLiveStockList.append({
                    "Item": a['Item'],
                    "Quantity": a['Quantity'],
                    "Unit": a['Unit'],
                    "BaseUnitQuantity": BaseUnitQuantity,
                    "OriginalBaseUnitQuantity": BaseUnitQuantity,
                    "Party": Party,
                    "IsDamagePieces":IsDamagePieces,
                    "CreatedBy":PurchaseReturndata['CreatedBy'],
                    
                    })
                    
                    O_LiveBatchesList.append({
                    
                    "ItemExpiryDate":date.today()+ datetime.timedelta(days = query2[0]['Days']),
                    "MRP": a['MRP'],
                    "Rate": a['Rate'],
                    "GST": a['GST'],
                    "SystemBatchDate": a['SystemBatchDate'],
                    "SystemBatchCode": a['SystemBatchCode'],
                    "BatchDate": a['BatchDate'],
                    "BatchCode": a['BatchCode'],
                    "OriginalBatchBaseUnitQuantity" : BaseUnitQuantity,
                    "O_BatchWiseLiveStockList" :O_BatchWiseLiveStockList                   
                    
                    })
                    O_BatchWiseLiveStockList=list()
                    
                   
                # print(GRNdata)
                PurchaseReturndata.update({"O_LiveBatchesList":O_LiveBatchesList}) 
                PurchaseReturn_Serializer = PurchaseReturnSerializer(data=PurchaseReturndata)
                # return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':'', 'Data':PurchaseReturn_Serializer.data})
                if PurchaseReturn_Serializer.is_valid():
                    PurchaseReturn_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Purchase Return Save Successfully', 'Data':[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  PurchaseReturn_Serializer.errors, 'Data':[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
    
    # GRN DELETE API 
    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                O_BatchWiseLiveStockData = O_BatchWiseLiveStock.objects.filter(PurchaseReturn_id=id).values('OriginalBaseUnitQuantity','BaseUnitQuantity')
              
                for a in O_BatchWiseLiveStockData:
                    if (a['OriginalBaseUnitQuantity'] != a['BaseUnitQuantity']) :
                        return JsonResponse({'StatusCode': 226, 'Status': True, 'Message': 'Return  Used in another Transaction', 'Data': []})   
                
                PurchaseReturn_Data = T_PurchaseReturn.objects.get(id=id)
                PurchaseReturn_Data.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Return Deleted Successfully', 'Data': []})
        except T_PurchaseReturn.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Record Not available', 'Data': []})
        except IntegrityError:
            return JsonResponse({'StatusCode': 226, 'Status': True, 'Message': 'Return Used in another Transaction', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
        
        
##################### Purchase Return Item View ###########################################        
        
class ReturnItemAddView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                query = M_Items.objects.filter(id=id)
                if query.exists():
                    # return JsonResponse({'query':  str(Itemsquery.query)})
                    Itemsdata = ItemSerializerSecond(query, many=True).data
                    # return JsonResponse({'query':  Itemsdata})
                    Itemlist = list()
                    InvoiceItems=list()
                    for a in Itemsdata:
                        Item=a['id']
                        Unitquery = MC_ItemUnits.objects.filter(Item_id=Item,IsDeleted=0)
                        if Unitquery.exists():
                            Unitdata = Mc_ItemUnitSerializerThird(Unitquery, many=True).data
                            ItemUnitDetails = list()
                            for c in Unitdata:
                                ItemUnitDetails.append({
                                "Unit": c['id'],
                                "BaseUnitQuantity": c['BaseUnitQuantity'],
                                "IsBase": c['IsBase'],
                                "UnitName": c['BaseUnitConversion'],
                            })
                        
                        MRPquery = M_MRPMaster.objects.filter(Item_id=Item).order_by('-id')[:3] 
                        if MRPquery.exists():
                            MRPdata = ItemMRPSerializerSecond(MRPquery, many=True).data
                            ItemMRPDetails = list()
                            
                            for d in MRPdata:
                                ItemMRPDetails.append({
                                "MRP": d['id'],
                                "MRPValue": d['MRP'],   
                            })
                        
                        GSTquery = M_GSTHSNCode.objects.filter(Item_id=Item).order_by('-id')[:3] 
                        if GSTquery.exists():
                            Gstdata = ItemGSTHSNSerializerSecond(GSTquery, many=True).data
                            ItemGSTDetails = list()
                            for e in Gstdata:
                                ItemGSTDetails.append({
                                "GST": e['id'],
                                "GSTPercentage": e['GSTPercentage'],   
                            }) 
                        InvoiceItems.append({
                            "Item": a['id'],
                            "ItemName": a['Name'],
                            "ItemUnitDetails": ItemUnitDetails, 
                            "ItemMRPDetails":ItemMRPDetails,
                            "ItemGSTDetails":ItemGSTDetails
                        })
                    
                    Itemlist.append({"InvoiceItems":InvoiceItems})    
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': Itemlist[0]})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Items Not available ', 'Data': []})
        except M_Items.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Items Not available', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})        



class ReturnItemBatchCodeAddView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request, id=0):
        try:
            with transaction.atomic():
                PurchaseReturndata = JSONParser().parse(request)
                ItemID = PurchaseReturndata['ItemID']
                BatchCode = PurchaseReturndata['BatchCode']
                if BatchCode != "":
                    query = TC_GRNItems.objects.filter(Item=ItemID,BatchCode=BatchCode).order_by('id')[:1]
                else:
                    query = TC_GRNItems.objects.filter(Item=ItemID).order_by('id')[:1]  
                if query.exists():
                    GRNItemsdata = TC_GRNItemsSerializerSecond(query, many=True).data
                    # return JsonResponse({'query':  Itemsdata})
                    GRMItems = list()
                    for a in GRNItemsdata:
                        Item =a['Item']['id']
                        Unitquery = MC_ItemUnits.objects.filter(Item_id=Item,IsDeleted=0)
                        if Unitquery.exists():
                            Unitdata = Mc_ItemUnitSerializerThird(Unitquery, many=True).data
                            ItemUnitDetails = list()
                            for c in Unitdata:
                                ItemUnitDetails.append({
                                "Unit": c['id'],
                                "BaseUnitQuantity": c['BaseUnitQuantity'],
                                "IsBase": c['IsBase'],
                                "UnitName": c['BaseUnitConversion'],
                            })
                        
                        MRPquery = M_MRPMaster.objects.filter(Item_id=Item).order_by('-id')[:3] 
                        if MRPquery.exists():
                            MRPdata = ItemMRPSerializerSecond(MRPquery, many=True).data
                            ItemMRPDetails = list()
                            
                            for d in MRPdata:
                                ItemMRPDetails.append({
                                "MRP": d['id'],
                                "MRPValue": d['MRP'],   
                            })
                        
                        GSTquery = M_GSTHSNCode.objects.filter(Item_id=Item).order_by('-id')[:3] 
                        if GSTquery.exists():
                            Gstdata = ItemGSTHSNSerializerSecond(GSTquery, many=True).data
                            ItemGSTDetails = list()
                            for e in Gstdata:
                                ItemGSTDetails.append({
                                "GST": e['id'],
                                "GSTPercentage": e['GSTPercentage'],   
                            }) 
                        
                        
                        GRMItems.append({
                            "Item": a['Item']['id'],
                            "ItemName": a['Item']['Name'],
                            "Quantity": a['Quantity'],
                            "MRP": a['MRP']['id'],
                            "MRPValue": a['MRPValue'],
                            "Rate": a['Rate'],
                            "TaxType": a['TaxType'],
                            "Unit": a['Unit']['id'],
                            "UnitName": a['Unit']['UnitID'],
                            "BaseUnitQuantity": a['BaseUnitQuantity'],
                            "GST": a['GST']['id'],
                            "GSTPercentage": a['GSTPercentage'],
                            "BasicAmount": a['BasicAmount'],
                            "GSTAmount": a['GSTAmount'],
                            "CGST": a['CGST'],
                            "SGST": a['SGST'],
                            "IGST": a['IGST'],
                            "CGSTPercentage": a['CGSTPercentage'],
                            "SGSTPercentage": a['SGSTPercentage'],
                            "IGSTPercentage": a['IGSTPercentage'],
                            "Amount": a['Amount'],
                            "BatchCode": a['BatchCode'],
                            "BatchDate": a['BatchDate'],
                            "DiscountType": a['DiscountType'],
                            "Discount": a['Discount'],
                            "DiscountAmount": a['DiscountAmount'],
                            "ItemUnitDetails": ItemUnitDetails, 
                            "ItemMRPDetails":ItemMRPDetails,
                            "ItemGSTDetails":ItemGSTDetails
                        })   
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': GRMItems})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Items Not available ', 'Data': []})
        except M_Items.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Items Not available', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})        
