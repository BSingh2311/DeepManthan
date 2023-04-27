from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import transaction
from rest_framework.parsers import JSONParser

from ..Views.V_TransactionNumberfun import GetMaxNumber, GetPrifix
from ..Serializer.S_Invoices import *
from ..Serializer.S_Orders import *

from ..models import  *


class OrderDetailsForInvoice(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    def post(self, request, id=0):
        try:
            with transaction.atomic():
               
                Orderdata = JSONParser().parse(request)
                FromDate = Orderdata['FromDate']
                Party = Orderdata['Party']
                Customer = Orderdata['Customer']
                POOrderIDs = Orderdata['OrderIDs']
                Order_list = POOrderIDs.split(",")
                OrderItemDetails = list()
                Orderdata = list()
               
                if POOrderIDs != '':
                    OrderQuery=T_Orders.objects.raw("SELECT T_Orders.Supplier_id id,M_Parties.Name SupplierName,sum(T_Orders.OrderAmount) OrderAmount ,T_Orders.Customer_id CustomerID FROM T_Orders join M_Parties on M_Parties.id=T_Orders.Supplier_id where T_Orders.id IN %s group by T_Orders.Supplier_id;",[Order_list])
                    OrderSerializedata = OrderSerializerForGrn(OrderQuery,many=True).data
                    OrderItemQuery=TC_OrderItems.objects.filter(Order__in=Order_list,IsDeleted=0).order_by('Item')
                    OrderItemSerializedata=TC_OrderItemSerializer(OrderItemQuery,many=True).data
                else:
                    query = T_Orders.objects.filter(OrderDate=FromDate,Supplier=Party,Customer=Customer)
                    Serializedata = OrderserializerforInvoice(query,many=True).data
                    Order_list = list()
                    for x in Serializedata:
                        Order_list.append(x['id'])
                        
                    OrderQuery=T_Orders.objects.raw("SELECT T_Orders.Supplier_id id,M_Parties.Name SupplierName,sum(T_Orders.OrderAmount) OrderAmount ,T_Orders.Customer_id CustomerID FROM T_Orders join M_Parties on M_Parties.id=T_Orders.Supplier_id where T_Orders.id IN %s group by T_Orders.Supplier_id;",[Order_list])
                    OrderSerializedata = OrderSerializerForGrn(OrderQuery,many=True)
                    OrderItemQuery=TC_OrderItems.objects.filter(Order__in=Order_list,IsDeleted=0).order_by('Item')
                    OrderItemSerializedata=TC_OrderItemSerializer(OrderItemQuery,many=True).data
                       
                # return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': OrderItemSerializedata})
                for b in OrderItemSerializedata:
                    
                    Item= b['Item']['id']
                    obatchwisestockquery= O_BatchWiseLiveStock.objects.filter(Item_id=Item,Party_id=Party,BaseUnitQuantity__gt=0)
                  
                    if obatchwisestockquery == "":
                        StockQtySerialize_data =[]
                    else:
                        
                        StockQtySerialize_data = StockQtyserializerForInvoice(obatchwisestockquery, many=True).data
                        
                        # return JsonResponse({'StatusCode': 200, 'Status': True, 'Data':StockQtySerialize_data[0]['LiveBatche']})
    
                        stockDatalist = list()
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
                                "MRP" : d['LiveBatche']['MRP']['MRP'],
                                "GST" : d['LiveBatche']['GST']['GSTPercentage'],
                                "UnitName":d['Unit']['BaseUnitConversion'], 
                                "BaseUnitQuantity":d['BaseUnitQuantity'],
                                  
                                })
                    query = MC_ItemUnits.objects.filter(Item_id=Item,IsDeleted=0)
                    # print(query.query)
                    if query.exists():
                        Unitdata = Mc_ItemUnitSerializerThird(query, many=True).data
                        UnitDetails = list()
                        for c in Unitdata:
                           
                            UnitDetails.append({
                            "Unit": c['id'],
                            "UnitName": c['BaseUnitConversion'],
                            "ConversionUnit": c['BaseUnitQuantity'],
                            "Unitlabel": c['UnitID']['Name']
                        })
                        # return JsonResponse({'StatusCode': 200, 'Status': True, 'Data':Unitdata})
                        
                    OrderItemDetails.append({
                         
                        "id": b['id'],
                        "Item": b['Item']['id'],
                        "ItemName": b['Item']['Name'],
                        "Quantity": b['Quantity'],
                        "MRP": b['MRP']['id'],
                        "MRPValue": b['MRP']['MRP'],
                        "Rate": b['Rate'],
                        "Unit": b['Unit']['id'],
                        "UnitName": b['Unit']['BaseUnitConversion'],
                        "ConversionUnit": b['Unit']['BaseUnitQuantity'],
                        "BaseUnitQuantity": b['BaseUnitQuantity'],
                        "GST": b['GST']['id'],
                        "HSNCode": b['GST']['HSNCode'],
                        "GSTPercentage": b['GST']['GSTPercentage'],
                        "Margin": b['Margin']['id'],
                        "MarginValue": b['Margin']['Margin'],
                        "BasicAmount": b['BasicAmount'],
                        "GSTAmount": b['GSTAmount'],
                        "CGST": b['CGST'],
                        "SGST": b['SGST'],
                        "IGST": b['IGST'],
                        "CGSTPercentage": b['CGSTPercentage'],
                        "SGSTPercentage": b['SGSTPercentage'],
                        "IGSTPercentage": b['IGSTPercentage'],
                        "Amount": b['Amount'],
                        "UnitDetails":UnitDetails,
                        "StockDetails":stockDatalist
                    })
                Orderdata.append({
                    "OrderIDs":Order_list,
                    "OrderItemDetails":OrderItemDetails
                   })         
            return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': Orderdata[0]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
        

class InvoiceListFilterView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request, id=0):
        try:
            with transaction.atomic():
                Invoicedata = JSONParser().parse(request)
                FromDate = Invoicedata['FromDate']
                ToDate = Invoicedata['ToDate']
                Customer = Invoicedata['Customer']
                Party = Invoicedata['Party']
               
                if(Customer == ''):
                    query = T_Invoices.objects.filter(InvoiceDate__range=[FromDate, ToDate], Party=Party)
                else:
                    query = T_Invoices.objects.filter(InvoiceDate__range=[FromDate, ToDate], Customer_id=Customer, Party=Party)
                   
                # return JsonResponse({'query': str(Orderdata.query)})
                if query:
                    Invoice_serializer = InvoiceSerializerSecond(query, many=True).data
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'','Data': Order_serializer})
                    InvoiceListData = list()
                    for a in Invoice_serializer:
                        Count = TC_LoadingSheetDetails.objects.filter(Invoice=a['id']).count()
                        if Count == 0:
                            LoadingSheetCreated = False 
                        else:
                            LoadingSheetCreated = True 
                        InvoiceListData.append({
                            "id": a['id'],
                            "InvoiceDate": a['InvoiceDate'],
                            "FullInvoiceNumber": a['FullInvoiceNumber'],
                            "CustomerID": a['Customer']['id'],
                            "Customer": a['Customer']['Name'],
                            "PartyID": a['Party']['id'],
                            "Party": a['Party']['Name'],
                            "GrandTotal": a['GrandTotal'],
                            "RoundOffAmount": a['RoundOffAmount'],
                            "LoadingSheetCreated": LoadingSheetCreated, 
                            "DriverName": a['Driver']['Name'],
                            "VehicleNo": a['Vehicle']['VehicleNumber'],
                            "Party": a['Party']['Name'],
                            "CreatedOn": a['CreatedOn'] 
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': InvoiceListData})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Record Not Found', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})


class InvoiceView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                Invoicedata = JSONParser().parse(request)
                Party = Invoicedata['Party']
                InvoiceDate = Invoicedata['InvoiceDate']
                # ==========================Get Max Invoice Number=====================================================
                a = GetMaxNumber.GetInvoiceNumber(Party,InvoiceDate)
                Invoicedata['InvoiceNumber'] = a
                b = GetPrifix.GetInvoicePrifix(Party)
                Invoicedata['FullInvoiceNumber'] = b+""+str(a)
                #================================================================================================== 
                InvoiceItems = Invoicedata['InvoiceItems']
                
                O_BatchWiseLiveStockList=list()
                for InvoiceItem in InvoiceItems:
                    O_BatchWiseLiveStockList.append({
                        "Quantity" : InvoiceItem['BatchID'],
                        "Item" : InvoiceItem['Item'],
                        "BaseUnitQuantity" : InvoiceItem['Quantity']
                    })
                        
                Invoicedata.update({"obatchwiseStock":O_BatchWiseLiveStockList}) 
                
                Invoice_serializer = InvoiceSerializer(data=Invoicedata)
                if Invoice_serializer.is_valid():
                    Invoice_serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'Invoice Save Successfully', 'Data':[]})
                return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': Invoice_serializer.errors, 'Data':[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
    
class InvoiceViewSecond(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication
    

    def get(self, request, id=0):
        try:
            with transaction.atomic():
                InvoiceQuery = T_Invoices.objects.filter(id=id)
                if InvoiceQuery.exists():
                    InvoiceSerializedata = InvoiceSerializerSecond(
                        InvoiceQuery, many=True).data
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': InvoiceSerializedata})
                    InvoiceData = list()
                    for a in InvoiceSerializedata:
                        InvoiceItemDetails = list()
                        for b in a['InvoiceItems']:
                            InvoiceItemDetails.append({
                                "Item": b['Item']['id'],
                                "ItemName": b['Item']['Name'],
                                "Quantity": b['Quantity'],
                                "MRP": b['MRP']['id'],
                                "MRPValue": b['MRP']['MRP'],
                                "Rate": b['Rate'],
                                "TaxType": b['TaxType'],
                                "UnitName": b['Unit']['BaseUnitConversion'],
                                "BaseUnitQuantity": b['BaseUnitQuantity'],
                                "GST": b['GST']['id'],
                                "GSTPercentage": b['GST']['GSTPercentage'],
                                "MarginValue": b['Margin']['Margin'],
                                "BasicAmount": b['BasicAmount'],
                                "GSTAmount": b['GSTAmount'],
                                "CGST": b['CGST'],
                                "SGST": b['SGST'],
                                "IGST": b['IGST'],
                                "CGSTPercentage": b['CGSTPercentage'],
                                "SGSTPercentage": b['SGSTPercentage'],
                                "IGSTPercentage": b['IGSTPercentage'],
                                "Amount": b['Amount'],
                                "BatchCode": b['BatchCode'],
                                "BatchDate": b['BatchDate'],
                            })
                            
                            InvoiceReferenceDetails = list()
                            for d in a['InvoicesReferences']:
                                InvoiceReferenceDetails.append({
                                    # "Invoice": d['Invoice'],
                                    "Order": d['Order']['id'],
                                    "FullOrderNumber": d['Order']['FullOrderNumber'],
                                })
                            
                        DefCustomerAddress = ''  
                        for ad in a['Customer']['PartyAddress']:
                            if ad['IsDefault'] == True :
                                DefCustomerAddress = ad['Address']
                                
                        DefPartyAddress = ''
                        for x in a['Party']['PartyAddress']:
                            if x['IsDefault'] == True :
                                DefPartyAddress = x['Address']
                    
                        InvoiceData.append({
                            "id": a['id'],
                            "InvoiceDate": a['InvoiceDate'],
                            "InvoiceNumber": a['InvoiceNumber'],
                            "FullInvoiceNumber": a['FullInvoiceNumber'],
                            "GrandTotal": a['GrandTotal'],
                            "RoundOffAmount":a['RoundOffAmount'],
                            "Customer": a['Customer']['id'],
                            "CustomerName": a['Customer']['Name'],
                            "CustomerGSTIN": a['Customer']['GSTIN'],
                            "Party": a['Party']['id'],
                            "PartyName": a['Party']['Name'],
                            "PartyGSTIN": a['Party']['GSTIN'],
                            "PartyFSSAINo": a['Party']['PartyAddress'][0]['FSSAINo'],
                            "CustomerFSSAINo": a['Customer']['PartyAddress'][0]['FSSAINo'],
                            "PartyState": a['Party']['State']['Name'],
                            "CustomerState": a['Customer']['State']['Name'],
                            "PartyAddress": DefPartyAddress,                            
                            "CustomerAddress": DefCustomerAddress,
                            "DriverName":a['Driver']['Name'],
                            "VehicleNo": a['Vehicle']['VehicleNumber'],
                            "CreatedOn" : a['CreatedOn'],
                            "InvoiceItems": InvoiceItemDetails,
                            "InvoicesReferences": InvoiceReferenceDetails,
                                                        
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': InvoiceData[0]})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Order Data Not available ', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                Invoicedata=T_Invoices.objects.all().filter(id=id)
                Invoicedataserializer=InvoiceSerializerForDelete(Invoicedata,many=True).data
                # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Invoice Delete Successfully', 'Data':Invoicedataserializer})
                
                for a in Invoicedataserializer[0]['InvoiceItems']:
                    BaseUnitQuantity11=UnitwiseQuantityConversion(a['Item'],a['Quantity'],a['Unit'],0,0,0,0).GetBaseUnitQuantity()
                    selectQuery=O_BatchWiseLiveStock.objects.filter(LiveBatche=a['LiveBatch']).values('BaseUnitQuantity')
                    UpdateQuery=O_BatchWiseLiveStock.objects.filter(LiveBatche=a['LiveBatch']).update(BaseUnitQuantity = int(selectQuery[0]['BaseUnitQuantity'] )+int(BaseUnitQuantity11))
                  
                Invoicedata = T_Invoices.objects.get(id=id)
                Invoicedata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Invoice Delete Successfully', 'Data':[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})   

class InvoiceNoView(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication
    @transaction.atomic()

    def post(self, request, id=0):
        try:
            with transaction.atomic():
                InVoice_Data = JSONParser().parse(request)  
                Party = InVoice_Data['PartyID']
                Customer = InVoice_Data['CustomerID']
                query = T_Invoices.objects.filter(Party=Party,Customer=Customer)
                if query.exists:
                    Invoice_Serializer = InvoiceSerializerSecond(query,many=True).data
                    InvoiceList = list()
                    for a in Invoice_Serializer:
                        InvoiceList.append({
                            "Invoice":a['id'],
                            "FullInvoiceNumber":a['FullInvoiceNumber'],
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': InvoiceList})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Record Not Found', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []}) 
        



##################### Purchase Return Invoice View ###########################################     
        
class InvoiceViewThird(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication
    
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                InvoiceQuery = T_Invoices.objects.filter(id=id)
                if InvoiceQuery.exists():
                    InvoiceSerializedata = InvoiceSerializerSecond(
                        InvoiceQuery, many=True).data
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': InvoiceSerializedata})
                    InvoiceData = list()
                    for a in InvoiceSerializedata:
                        InvoiceItemDetails = list()
                        for b in a['InvoiceItems']:
                            ChildItem= b['Item']['id']
                            Unitquery = MC_ItemUnits.objects.filter(Item_id=ChildItem,IsDeleted=0)
                            # print(query.query)
                            if Unitquery.exists():
                                Unitdata = Mc_ItemUnitSerializerThird(Unitquery, many=True).data
                                ItemUnitDetails = list()
                               
                                for c in Unitdata:
                                    ItemUnitDetails.append({
                                    "Unit": c['id'],
                                    "UnitName": c['BaseUnitConversion'],
                                })
                                    
                            MRPquery = M_MRPMaster.objects.filter(Item_id=ChildItem).order_by('-id')[:3] 
                            # print(query.query)
                            if MRPquery.exists():
                                MRPdata = ItemMRPSerializerSecond(MRPquery, many=True).data
                                ItemMRPDetails = list()
                               
                                for d in MRPdata:
                                    ItemMRPDetails.append({
                                    "MRP": d['id'],
                                    "MRPValue": d['MRP'],   
                                })
                                    
                            GSTquery = M_GSTHSNCode.objects.filter(Item_id=ChildItem).order_by('-id')[:3] 
                            # print(query.query)
                            if GSTquery.exists():
                                Gstdata = ItemGSTHSNSerializerSecond(GSTquery, many=True).data
                                ItemGSTDetails = list()
                                
                                for e in Gstdata:
                                    ItemGSTDetails.append({
                                    "GST": e['id'],
                                    "GSTPercentage": e['GSTPercentage'],   
                                })                
                                    
                            InvoiceItemDetails.append({
                                "Item": b['Item']['id'],
                                "ItemName": b['Item']['Name'],
                                "Quantity": b['Quantity'],
                                "MRP": b['MRP']['id'],
                                "MRPValue": b['MRP']['MRP'],
                                "Rate": b['Rate'],
                                "TaxType": b['TaxType'],
                                "Unit": b['Unit']['id'],
                                "UnitName": b['Unit']['BaseUnitConversion'],
                                "BaseUnitQuantity": b['BaseUnitQuantity'],
                                "GST": b['GST']['id'],
                                "GSTPercentage": b['GST']['GSTPercentage'],
                                "BasicAmount": b['BasicAmount'],
                                "GSTAmount": b['GSTAmount'],
                                "CGST": b['CGST'],
                                "SGST": b['SGST'],
                                "IGST": b['IGST'],
                                "CGSTPercentage": b['CGSTPercentage'],
                                "SGSTPercentage": b['SGSTPercentage'],
                                "IGSTPercentage": b['IGSTPercentage'],
                                "Amount": b['Amount'],
                                "BatchCode": b['BatchCode'],
                                "BatchDate": b['BatchDate'],
                                "ItemUnitDetails":ItemUnitDetails,
                                "ItemMRPDetails":ItemMRPDetails,
                                "ItemGSTDetails":ItemGSTDetails,
                                
                            })
                            
                        InvoiceData.append({
                            "id": a['id'],
                            "InvoiceDate": a['InvoiceDate'],
                            "InvoiceNumber": a['InvoiceNumber'],
                            "FullInvoiceNumber": a['FullInvoiceNumber'],
                            "GrandTotal": a['GrandTotal'],
                            "RoundOffAmount":a['RoundOffAmount'],
                            "Customer": a['Customer']['id'],
                            "CustomerName": a['Customer']['Name'],
                            "Party": a['Party']['id'],
                            "PartyName": a['Party']['Name'],
                            "CreatedOn" : a['CreatedOn'],
                            "InvoiceItems": InvoiceItemDetails,
                                               
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': InvoiceData[0]})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Order Data Not available ', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})                                      
                              
class BulkInvoiceView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                Invoicedata = JSONParser().parse(request)
                # Party = Invoicedata['Party']
                # InvoiceDate = Invoicedata['InvoiceDate']
                # # ==========================Get Max Invoice Number=====================================================
                # a = GetMaxNumber.GetInvoiceNumber(Party,InvoiceDate)
                # Invoicedata['InvoiceNumber'] = a
                # b = GetPrifix.GetInvoicePrifix(Party)
                # Invoicedata['FullInvoiceNumber'] = b+""+str(a)
                # #================================================================================================== 
                # InvoiceItems = Invoicedata['InvoiceItems']
                aa=""
                for Invoice in Invoicedata:
                    print(Invoice)
                    CustomerMapping=M_PartyCustomerMappingMaster.objects.filter(MapCustomer=Invoice['Customer'],Party=Invoice['Party']).values("Customer")
                    if CustomerMapping.exists():
                        Invoice['Customer']=CustomerMapping[0]['Customer']
                    else:
                        aa='1'+'! Customer'    
                    
                    for InvoiceItems in Invoice['InvoiceItems']:

                        ItemMapping=M_ItemMappingMaster.objects.filter(MapItem=InvoiceItems['Item'],Party=Invoice['Party']).values("Item")
                        UnitMapping=M_UnitMappingMaster.objects.filter(MapUnit=InvoiceItems['Unit'],Party=Invoice['Party']).values("Unit")
                        print(ItemMapping)
                        if ItemMapping.exists():
                            InvoiceItems['Item'] = ItemMapping[0]["Item"]
                        else:
                            aa='1'+'!Item'
                        if UnitMapping.exists():
                            print('abbbbbbbbbbbbbbbbb')
                            MC_UnitID=MC_ItemUnits.objects.filter(UnitID=UnitMapping[0]["Unit"],Item=ItemMapping[0]["Item"],IsDeleted=0).values("id")
                            
                            InvoiceItems['Unit'] = MC_UnitID[0]["id"]
                        else:
                            aa='1'+'! Unit'
                    print('cccccccc')        
                    bb=aa.split('!')
                    print('dddddd')
                    if bb[0]=='1':
                        print('eeeeeee')
                        return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': bb[1]+" Data Mapping Missing", 'Data':[]})
                    
                        print(Invoicedata)
                    else:
                        return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': "", 'Data':Invoicedata})
                        Invoice_serializer = BulkInvoiceSerializer(data=Invoicedata , many=True )
                        if Invoice_serializer.is_valid():
                            print('vvvvvvvvv')
                            Invoice_serializer.save()
                        else:    
                             return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': Invoice_serializer.errors, 'Data':[]})
                return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'Invoice Save Successfully', 'Data':[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
               
