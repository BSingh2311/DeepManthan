from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_GRNs import *
from ..Serializer.S_Challan import *
from ..Serializer.S_Bom import * 
from ..Serializer.S_Invoices import * 
from ..Views.V_TransactionNumberfun import GetMaxNumber, GetPrifix
from ..models import  *

class ChallanItemsView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication
    @transaction.atomic()
    def post(self, request, id=0 ):
        ChallanitemsData = JSONParser().parse(request)
        try:
            with transaction.atomic():
                Company=ChallanitemsData['Company']
                Query = MC_BillOfMaterialItems.objects.filter(BOM__IsVDCItem=1,BOM__Company=Company).select_related('BOM','Item').values('Item').distinct()
                CustomPrint(Query.query)
                ItemList = list()
                for a in Query:
                    ItemList.append(a['Item'])
                y=tuple(ItemList)
                Itemsquery = M_Items.objects.filter(id__in=y,isActive=1)
                CustomPrint(Itemsquery.query)
                Itemsdata = M_ItemsSerializer01(Itemsquery,many=True).data    
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data':Itemsdata})      
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})
        
class ChallanItemStockView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication
    @transaction.atomic()
    def post(self, request, id=0 ):
        ChallanItemData = JSONParser().parse(request)
        try:
            with transaction.atomic():
                Item = ChallanItemData['Item']
                Party = ChallanItemData['Party']
                        
                obatchwisestockquery= O_BatchWiseLiveStock.objects.filter(Item_id=Item,Party_id=Party,BaseUnitQuantity__gt=0)                
                if obatchwisestockquery == "":                    
                    StockQtySerialize_data =[]
                else:                     
                    StockQtySerialize_data = StockQtyserializerForInvoice(obatchwisestockquery, many=True).data
                    stockDatalist = list()
                    # CustomPrint(StockQtySerialize_data)
                    for d in StockQtySerialize_data:
                        
                        stockDatalist.append({
                            "id": d['id'],
                            "Item":d['Item']['id'],
                            "BatchDate":d['LiveBatche']['BatchDate'],
                            "BatchCode":d['LiveBatche']['BatchCode'],
                            "SystemBatchDate":d['LiveBatche']['SystemBatchDate'],
                            "SystemBatchCode":d['LiveBatche']['SystemBatchCode'],
                            "LiveBatche" : d['LiveBatche']['id'],
                            "LiveBatcheMRPID" : d['LiveBatche']['MRP']['id'],
                            "LiveBatcheGSTID" : d['LiveBatche']['GST']['id'],
                            "Rate":d['LiveBatche']['Rate'],
                            "MRP" : d['LiveBatche']['MRP']['id'],
                            "MRPValue": d['LiveBatche']['MRP']['MRP'],
                            "GSTPercentage" : d['LiveBatche']['GST']['GSTPercentage'],
                            "GST": d['LiveBatche']['GST']['id'],
                            # "HSNCode": d['LiveBatche']['GST']['HSNCode'],
                            "GSTPercentage": d['LiveBatche']['GST']['GSTPercentage'],
                            "UnitName":d['Unit']['UnitID'], 
                            "Unit":d['Unit']['BaseUnitConversion'], 
                            "BaseUnitQuantity":d['BaseUnitQuantity'], 
                            }) 
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': stockDatalist})   
                    # CustomPrint(stockDatalist)        
        except Exception as e:
            
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})
        
class ChallanView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request, id=0):
        Challandata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                GRN = Challandata['GRN']
                if GRN == "":
                    ChallanDate = Challandata['ChallanDate']
                    Party = Challandata['Party']
                    a = GetMaxNumber.GetChallanNumber(Party,ChallanDate)
                    Challandata['ChallanNumber'] = a
                    b = GetPrifix.GetChallanPrifix(Party)
                    Challandata['FullChallanNumber'] = str(b)+""+str(a)
                    # CustomPrint(Challandata)
                    ChallanItems = Challandata['ChallanItems']
                    # CustomPrint(ChallanItems)
                    # CustomPrint("Shruti")
                    BatchWiseLiveStockList=list()
                    # CustomPrint(ChallanItems)
                    for ChallanItem in ChallanItems:
                        # CustomPrint(ChallanItem['Item'])
                        # CustomPrint(ChallanItem['Quantity'])
                        # CustomPrint(ChallanItem['BaseUnitQuantity'])
                        # CustomPrint(ChallanItem['BatchID'])
                        CustomPrint(Challandata['Customer'])
                        # CustomPrint("FFFFFFFF")
                        BatchWiseLiveStockList.append({
                            "Item" : ChallanItem['Item'],
                            "Quantity" : ChallanItem['Quantity'],
                            "BaseUnitQuantity" : ChallanItem['BaseUnitQuantity'],
                            "LiveBatche" : ChallanItem['BatchID'],
                            # "Item" : ChallanItem['Item'],
                            "Party" : Challandata['Customer'],
                            # "Customer:":Challandata['Customer'],
                        })
                    # CustomPrint(BatchWiseLiveStockList)
                    Challandata.update({"BatchWiseLiveStockGRNID":BatchWiseLiveStockList}) 
                    # CustomPrint(Challandata)
                    Challan_serializer = ChallanSerializer(data=Challandata) 
                    # CustomPrint(Challan_serializer)                  
                    if Challan_serializer.is_valid():
                        # return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': Challan_serializer.data, 'Data':[]})
                        Challan_serializer.save()
                        return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'Challan Save Successfully', 'Data':[]})
                    return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': Challan_serializer.errors, 'Data':[]})
                else:
   
                    GRNdata = T_GRNs.objects.get(id=GRN)
                    GRN_serializer = T_GRNSerializerForGETSecond(GRNdata).data
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': GRN_serializer})
                    GRNItemListData = list()
                    for b in GRN_serializer['GRNItems']:
                        GRNItemListData.append({
                            "Item": b['Item']['id'],
                            "ItemName": b['Item']['Name'],
                            "Quantity": b['Quantity'],
                            "Unit": b['Unit']['id'],
                            "UnitName": b['Unit']['BaseUnitConversion'],
                            "BaseUnitQuantity": b['BaseUnitQuantity'],
                            "MRP": b['MRP'],
                            "ReferenceRate": b['ReferenceRate'],
                            "Rate": b['Rate'],
                            "BasicAmount": b['BasicAmount'],
                            "TaxType": b['TaxType'],
                            "GST": b['GST']['id'],
                            "GSTPercentage": b['GST']['GSTPercentage'],
                            "HSNCode": b['GST']['HSNCode'],
                            "GSTAmount": b['GSTAmount'],
                            "Amount": b['Amount'],
                            "DiscountType": b['DiscountType'],
                            "Discount": b['Discount'],
                            "DiscountAmount": b['DiscountAmount'],
                            "CGST": b['CGST'],
                            "SGST": b['SGST'],
                            "IGST": b['IGST'],
                            "CGSTPercentage": b['CGSTPercentage'],
                            "SGSTPercentage": b['SGSTPercentage'],
                            "IGSTPercentage": b['IGSTPercentage'],
                            "BatchDate": b['BatchDate'],
                            "BatchCode": b['BatchCode'],
                            "SystemBatchDate": b['SystemBatchDate'],
                            "SystemBatchCode": b['SystemBatchCode'],                            
                        })
                    GRNListData = list()
                    a = GRN_serializer
                    GRNListData.append({
                        "GRN": a['id'],
                        "ChallanDate": a['GRNDate'],
                        "Party": a['Customer']['id'],
                        "PartyName": a['Customer']['Name'],
                        "GrandTotal": a['GrandTotal'],
                        "Customer": a['Party']['id'],
                        "CustomerName": a['Party']['Name'],
                        "CreatedBy": a['CreatedBy'],
                        "UpdatedBy": a['UpdatedBy'],
                        "RoundOffAmount":"",
                        "ChallanItems": GRNItemListData,
                        "BatchWiseLiveStockGRNID":a['BatchWiseLiveStockGRNID']
                    })
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': GRNListData[0]})
                    Party = GRNListData[0]['Party']
                    ChallanDate = GRNListData[0]['ChallanDate']
                    # ==========================Get Max Invoice Number=====================================================
                    a = GetMaxNumber.GetChallanNumber(Party,ChallanDate)
                    GRNListData[0]['ChallanNumber'] = a
                    b = GetPrifix.GetChallanPrifix(Party)
                    GRNListData[0]['FullChallanNumber'] = str(b)+""+str(a)
                    #==================================================================================================
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': GRNListData[0]}) 
                    Challan_serializer = ChallanSerializer(data=GRNListData[0])
                    if Challan_serializer.is_valid():
                        # return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': Challan_serializer.data, 'Data':[]})
                        Challan_serializer.save()
                        return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'Challan Save Successfully', 'Data':[]})
                    return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': Challan_serializer.errors, 'Data':[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':Exception(e), 'Data': []})
 
 
        
    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                Invoicedata=T_Challan.objects.all().filter(id=id)
                Invoicedataserializer=ChallanSerializerForDelete(Invoicedata,many=True).data
                # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Invoice Delete Successfully', 'Data':Invoicedataserializer})
                
                for a in Invoicedataserializer[0]['ChallanItems']:
                    BaseUnitQuantity11=UnitwiseQuantityConversion(a['Item'],a['Quantity'],a['Unit'],0,0,0,0).GetBaseUnitQuantity()
                    # return JsonResponse({'StatusCode': 200, 'Data':BaseUnitQuantity11})
                    selectQuery=O_BatchWiseLiveStock.objects.filter(LiveBatche=a['LiveBatch']).values('BaseUnitQuantity')
                    # return JsonResponse({'StatusCode': 200,'Data1':a['LiveBatch'],'Data2':BaseUnitQuantity11, 'Data3':selectQuery[0]['BaseUnitQuantity']})
                    UpdateQuery=O_BatchWiseLiveStock.objects.filter(LiveBatche=a['LiveBatch']).update(BaseUnitQuantity = float(selectQuery[0]['BaseUnitQuantity'])+float(BaseUnitQuantity11))
                Invoicedata = T_Challan.objects.get(id=id)
                Invoicedata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Challan Delete Successfully', 'Data':[]})
        except T_Challan.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Challan Not available', 'Data': []})
        except IntegrityError:   
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Challan used in another table', 'Data': []})


class ChallanListFilterView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request, id=0):
        Challandata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                FromDate = Challandata['FromDate']
                ToDate = Challandata['ToDate']
                Customer = Challandata['Customer']
                Party = Challandata['Party']
                if(Customer == ''):
                    query = T_Challan.objects.filter(ChallanDate__range=[FromDate, ToDate], Party=Party)
                else:
                    query = T_Challan.objects.filter(ChallanDate__range=[FromDate, ToDate], Customer_id=Customer, Party=Party) 
                    
                if query:
                    Challan_serializer = ChallanSerializerList(query, many=True).data
                    ChallanListData = list()
                    for a in Challan_serializer:
                        ChallanListData.append({
                            "id": a['id'],
                            "ChallanDate": a['ChallanDate'],
                            "FullChallanNumber": a['FullChallanNumber'],
                            "CustomerID": a['Customer']['id'],
                            "Customer": a['Customer']['Name'],
                            "PartyID": a['Party']['id'],
                            "Party": a['Party']['Name'],
                            "GrandTotal": a['GrandTotal'],
                            "CreatedOn": a['CreatedOn'],
                            "POType":3
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': ChallanListData})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Record Not Found', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})        
        
        
class DemandDetailsForChallan(CreateAPIView):
        
    permission_classes = (IsAuthenticated,)   

    def post(self, request, id=0):
        try:
            with transaction.atomic():
               
                Demanddata = JSONParser().parse(request)
                # CustomPrint(Demanddata)
                # Party = Demanddata['Party']                
                DemandIDs = Demanddata['DemandID']
                DemandDate=Demanddata['DemandDate']
                # CustomPrint(DemandDate)
                # Demand_list = DemandIDs.split(",")    
                Demand_list = DemandIDs              
                Demanddata = list() 
                for DemandID in Demand_list: 
                    DemandItemDetails = list()
                    DemandItemQuery=TC_DemandItems.objects.raw(f'''SELECT 1 as id,TC_DemandItems.ID DemandID,M_items.id ItemID,M_Items.Name ItemName,TC_DemandItems.Quantity,Rate,Unit_id,
                    MC_ItemUnits.BaseUnitConversion,MC_ItemUnits.UnitID_id MUnitID,MC_ItemUnits.BaseUnitQuantity ConversionUnit,TC_DemandItems.BaseUnitQuantity,
                    TC_DemandItems.GST_id,M_GSTHSNCode.HSNCode,
                    TC_DemandItems.GSTAmount,TC_DemandItems.CGST,TC_DemandItems.SGST,TC_DemandItems.IGST,TC_DemandItems.CGSTPercentage,TC_DemandItems.SGSTPercentage,
                    TC_DemandItems.IGSTPercentage,TC_DemandItems.Amount,TC_DemandItems.BasicAmount, 
                    M_Parties.Name CustomerName,M_Parties.PAN,
                    T_Demands.DemandDate,M_Parties.id CustomerID,M_Parties.GSTIN,T_Demands.FullDemandNumber FROM  TC_DemandItems
                    JOIN T_Demands ON T_Demands.id=TC_DemandItems.Demand_id
                    JOIN M_Parties on M_Parties.id=T_Demands.Customer_id
                    JOIN M_items ON M_items.id=TC_demandItems.Item_id
                    JOIN MC_ItemUnits on MC_ItemUnits.id=TC_DemandItems.Unit_id
                    JOIN M_GSTHSNCode on M_GSTHSNCode.id=TC_DemandItems.GST_id
                    WHERE TC_DemandItems.Demand_id={DemandIDs} and TC_DemandItems.IsDeleted=0''')
                    CustomPrint(DemandItemQuery.query)
                            
                    for b in DemandItemQuery:                       
                        CustomPrint(b)
                        Customer=b.CustomerID
                        Item= b.ItemID                         
                        obatchwisestockquery= O_BatchWiseLiveStock.objects.raw(f'''SELECT 1 as id ,BatchDate,BaseUnitConversion,BatchCode,SystemBatchDate,SystemBatchCode,Round(GetTodaysDateRate({Item},'{DemandDate}',{Customer},0,2),2) AS Rate, O_BatchWiseLiveStock.id, O_BatchWiseLiveStock.Quantity, O_BatchWiseLiveStock.OriginalBaseUnitQuantity, O_BatchWiseLiveStock.BaseUnitQuantity, O_BatchWiseLiveStock.IsDamagePieces, O_BatchWiseLiveStock.CreatedBy,
                        O_BatchWiseLiveStock.CreatedOn, O_BatchWiseLiveStock.GRN_id, O_BatchWiseLiveStock.InterBranchInward_id, 
                        O_BatchWiseLiveStock.Item_id ItemID, O_BatchWiseLiveStock.LiveBatche_id, O_BatchWiseLiveStock.Party_id, 
                        O_BatchWiseLiveStock.Production_id, O_BatchWiseLiveStock.PurchaseReturn_id, O_BatchWiseLiveStock.Unit_id,O_LiveBatches.GST_id LiveBatcheGSTID,
                        O_BatchWiseLiveStock.BaseUnitQuantity ,(case when O_LiveBatches.GST_id is null then O_LiveBatches.GSTPercentage else M_GSTHSNCode.GSTPercentage end )GST
                        FROM O_BatchWiseLiveStock left  join O_LiveBatches on O_BatchWiseLiveStock.LiveBatche_id=O_LiveBatches.id 
                        left join MC_ItemUnits on MC_ItemUnits.id=O_BatchWiseLiveStock.Unit_id
                        left join M_GSTHSNCode on M_GSTHSNCode.id=O_LiveBatches.GST_id
                        WHERE O_BatchWiseLiveStock.BaseUnitQuantity > 0 AND O_BatchWiseLiveStock.Item_id = {Item} AND 
                        O_BatchWiseLiveStock.Party_id = {Customer}''')
                        CustomPrint(obatchwisestockquery.query)     
                        stockDatalist = list()
                        if not obatchwisestockquery:
                            stockDatalist =[]
                        else:   
                            for d in obatchwisestockquery:
                                stockDatalist.append({
                                    "id": d.id,
                                    "Item":d.ItemID,
                                    "BatchDate":d.BatchDate,
                                    "BatchCode":d.BatchCode,
                                    "SystemBatchDate":d.SystemBatchDate,
                                    "SystemBatchCode":d.SystemBatchCode,   
                                    "LiveBatcheGSTID" : d.LiveBatcheGSTID,
                                    "LiveBatche_id":d.LiveBatche_id,
                                    "Rate":round(d.Rate,2),                                   
                                    "GSTPercentage" : d.GST,
                                    "UnitName":d.BaseUnitConversion, 
                                    "BaseUnitQuantity":d.BaseUnitQuantity,                                    
                                    })  
                        DemandItemDetails.append({
                                            
                            "id": b.id,
                            "Item": b.ItemID,
                            "ItemName": b.ItemName,
                            "Quantity": b.Quantity,                            
                            "Rate": b.Rate,
                            "Unit": b.Unit_id,
                            "UnitName": b.BaseUnitConversion,
                            "DeletedMCUnitsUnitID": b.MUnitID,
                            "ConversionUnit": b.ConversionUnit,
                            "BaseUnitQuantity": b.BaseUnitQuantity,
                            "GST": b.GST_id,          
                            "HSNCode": b.HSNCode,                           
                            "BasicAmount": b.BasicAmount,
                            "GSTAmount": b.GSTAmount,
                            "CGST": b.CGST,
                            "SGST": b.SGST,
                            "IGST": b.IGST,
                            "CGSTPercentage": b.CGSTPercentage,
                            "SGSTPercentage": b.SGSTPercentage,
                            "IGSTPercentage": b.IGSTPercentage,
                            "Amount": b.Amount,                           
                                    # "UnitDetails":UnitDropdown(b.ItemID,Customer,0),
                            "StockDetails":stockDatalist
                            })
                        Demanddata.append({
                                "DemandIDs":DemandIDs,
                                "DemandDate" :  b.DemandDate,
                                "CustomerName" : b.CustomerName,                        
                                "CustomerPAN" : b.PAN,
                                "CustomerGSTIN" : b.GSTIN,
                                "CustomerID" : Customer,
                                "DemandNumber" : b.FullDemandNumber,
                                "DemandItemDetails":DemandItemDetails
                            })
                log_entry = create_transaction_logNew(request, Demanddata, 0,0,32,0,0,0,Customer)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': Demanddata[0]})
        except Exception as e:
                log_entry = create_transaction_logNew(request, 0, 0,'DemandDetailsForChallan:'+str (Exception(e)),33,0)
                return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})