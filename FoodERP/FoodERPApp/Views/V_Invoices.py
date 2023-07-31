from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import transaction
from rest_framework.parsers import JSONParser
from ..Views.V_TransactionNumberfun import GetMaxNumber, GetPrifix
from ..Serializer.S_Invoices import *
from ..Serializer.S_Orders import *
from ..Serializer.S_BankMaster import * 
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
                    obatchwisestockquery= O_BatchWiseLiveStock.objects.filter(Item_id=Item,Party_id=Party,BaseUnitQuantity__gt=0,IsDamagePieces=0)
                    # print(obatchwisestockquery.query)
                  
                    
                    if obatchwisestockquery == "":
                        StockQtySerialize_data =[]
                    else:
                        
                        StockQtySerialize_data = StockQtyserializerForInvoice(obatchwisestockquery, many=True).data
                        
                        # return JsonResponse({'StatusCode': 200, 'Status': True, 'Data':StockQtySerialize_data})
    
                        stockDatalist = list()
                        for d in StockQtySerialize_data:
                            Rate=RateCalculationFunction(d['LiveBatche']['id'],d['Item']['id'],Customer,0,d['Unit']["UnitID"]["id"],0,0).RateWithGST()
                           
                            if(d['LiveBatche']['MRP']['id'] is None):
                                MRPValue=d['LiveBatche']['MRPValue']
                            else:
                                MRPValue=d['LiveBatche']['MRP']['MRP']
                            
                            if(d['LiveBatche']['GST']['id'] is None):
                                GSTPercentage=d['LiveBatche']['GSTPercentage']
                            else:
                                GSTPercentage=d['LiveBatche']['GST']['GSTPercentage']
                            
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
                                "Rate":Rate[0]["NoRatewithOutGST"],
                                "MRP" : MRPValue,
                                "GST" : GSTPercentage,
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
                    # =====================Current Discount================================================
                    TodaysDiscount = DiscountMaster(
                        b['Item']['id'], Party, date.today(),Customer).GetTodaysDateDiscount()

                    DiscountType = TodaysDiscount[0]['DiscountType']
                    Discount = TodaysDiscount[0]['TodaysDiscount']

                    OrderItemDetails.append({
                         
                        "id": b['id'],
                        "Item": b['Item']['id'],
                        "ItemName": b['Item']['Name'],
                        "Quantity": b['Quantity'],
                        "MRP": b['MRP']['id'],
                        "MRPValue": b['MRPValue'],
                        "Rate": b['Rate'],
                        "Unit": b['Unit']['id'],
                        "UnitName": b['Unit']['BaseUnitConversion'],
                        "ConversionUnit": b['Unit']['BaseUnitQuantity'],
                        "BaseUnitQuantity": b['BaseUnitQuantity'],
                        "GST": b['GST']['id'],
                        "HSNCode": b['GST']['HSNCode'],
                        "GSTPercentage": b['GSTPercentage'],
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
                        "DiscountType" : DiscountType,
                        "Discount" : Discount,
                        "UnitDetails":UnitDropdown(b['Item']['id'],Customer,0),
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
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'','Data': Invoice_serializer})
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
                            "CreatedOn": a['CreatedOn'],
                            "InvoiceUploads" : a["InvoiceUploads"]
                             
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
                    # print(InvoiceItem['Quantity'])
                    BaseUnitQuantity=UnitwiseQuantityConversion(InvoiceItem['Item'],InvoiceItem['Quantity'],InvoiceItem['Unit'],0,0,0,0).GetBaseUnitQuantity()
                    InvoiceItem['BaseUnitQuantity'] =  round(BaseUnitQuantity,3) 
                    QtyInNo=UnitwiseQuantityConversion(InvoiceItem['Item'],InvoiceItem['Quantity'],InvoiceItem['Unit'],0,0,1,0).ConvertintoSelectedUnit()
                    InvoiceItem['QtyInNo'] =  float(QtyInNo)
                    QtyInKg=UnitwiseQuantityConversion(InvoiceItem['Item'],InvoiceItem['Quantity'],InvoiceItem['Unit'],0,0,2,0).ConvertintoSelectedUnit()
                    InvoiceItem['QtyInKg'] =  float(QtyInKg)
                    QtyInBox=UnitwiseQuantityConversion(InvoiceItem['Item'],InvoiceItem['Quantity'],InvoiceItem['Unit'],0,0,4,0).ConvertintoSelectedUnit()
                    InvoiceItem['QtyInBox'] = float(QtyInBox)
                    
                    O_BatchWiseLiveStockList.append({
                        "Quantity" : InvoiceItem['BatchID'],
                        "Item" : InvoiceItem['Item'],
                        "BaseUnitQuantity" : InvoiceItem['BaseUnitQuantity']
                    })
                Invoicedata.update({"obatchwiseStock":O_BatchWiseLiveStockList}) 
                Invoice_serializer = InvoiceSerializer(data=Invoicedata)
                if Invoice_serializer.is_valid():
                    Invoice_serializer.save()
                    LastInsertId = (T_Invoices.objects.last()).id
                    return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'Invoice Save Successfully','InvoiceID':LastInsertId, 'Data':[]})
                return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': Invoice_serializer.errors, 'Data':[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': Exception(e), 'Data': []})
    
class InvoiceViewSecond(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    
    # authentication__Class = JSONWebTokenAuthentication

#     def get(self, request, id=0):
#         try:
#             with transaction.atomic():
#                 InvoiceQuery = T_Invoices.objects.filter(id=id)
#                 if InvoiceQuery.exists():
#                     query = TC_InvoiceItems.objects.raw('''SELECT TC_InvoiceItems.id,TC_InvoiceItems.Item_id,M_Items.Name ItemName,Sum(TC_InvoiceItems.Quantity)Quantity,TC_InvoiceItems.MRP_id,TC_InvoiceItems.MRPValue,TC_InvoiceItems.Rate,TC_InvoiceItems.TaxType,TC_InvoiceItems.Unit_id,M_Units.Name UnitName,Sum(TC_InvoiceItems.BaseUnitQuantity)BaseUnitQuantity,TC_InvoiceItems.GST_id,TC_InvoiceItems.GSTPercentage,SUM(TC_InvoiceItems.BasicAmount)BasicAmount, SUM(TC_InvoiceItems.GSTAmount)GSTAmount,SUM(TC_InvoiceItems.CGST)CGST, SUM(TC_InvoiceItems.SGST)SGST, SUM(TC_InvoiceItems.IGST)IGST, TC_InvoiceItems.CGSTPercentage, TC_InvoiceItems.SGSTPercentage, TC_InvoiceItems.IGSTPercentage, SUM(TC_InvoiceItems.Amount)Amount,  TC_InvoiceItems.BatchCode,TC_InvoiceItems.BatchDate,M_GSTHSNCode.HSNCode,SUM(TC_InvoiceItems.Discount)Discount, SUM(TC_InvoiceItems.DiscountAmount)DiscountAmount,SUM(TC_InvoiceItems.QtyInBox)QtyInBox, SUM(TC_InvoiceItems.QtyInKg)QtyInKg, SUM(TC_InvoiceItems.QtyInNo)QtyInNo FROM TC_InvoiceItems 
# JOIN M_Items on M_Items.id=TC_InvoiceItems.Item_id
# JOIN M_MRPMaster on M_MRPMaster.id=TC_InvoiceItems.MRP_id
# JOIN MC_ItemUnits on  MC_ItemUnits.id= TC_InvoiceItems.Unit_id
# JOIN M_Units on M_Units.id=MC_ItemUnits.UnitID_id
# JOIN M_GSTHSNCode on M_GSTHSNCode.id = TC_InvoiceItems.GST_id
# JOIN O_LiveBatches on O_LiveBatches.id = TC_InvoiceItems.LiveBatch_id
# where tc_invoiceitems.Invoice_id=%s Group By M_Items.id,TC_InvoiceItems.MRPValue ''',([id]))
#                     # print(str(query.query))
#                     InvoiceItemSerializer = ChildInvoiceItemSerializer(query, many=True).data
#                     InvoiceItemDetails = list()
#                     for b in InvoiceItemSerializer:
#                         aaaa=UnitwiseQuantityConversion(b['Item_id'],b['Quantity'],b['Unit_id'],0,0,0,0).GetConvertingBaseUnitQtyBaseUnitName()
#                         InvoiceItemDetails.append({
#                             "Item": b['Item_id'],
#                             "ItemName": b['ItemName'],
#                             "Quantity": b['Quantity'],
#                             "MRP": b['MRP_id'],
#                             "MRPValue": b['MRPValue'],
#                             "Rate": b['Rate'],
#                             "UnitName": aaaa,
#                             "BaseUnitQuantity": b['BaseUnitQuantity'],
#                             "GST": b['GST_id'],
#                             "GSTPercentage": b['GSTPercentage'],
#                             "BasicAmount": b['BasicAmount'],
#                             "GSTAmount": b['GSTAmount'],
#                             "CGST": b['CGST'],
#                             "SGST": b['SGST'],
#                             "IGST": b['IGST'],
#                             "CGSTPercentage": b['CGSTPercentage'],
#                             "SGSTPercentage": b['SGSTPercentage'],
#                             "IGSTPercentage": b['IGSTPercentage'],
#                             "Amount": b['Amount'],
#                             "BatchCode": b['BatchCode'],
#                             "BatchDate": b['BatchDate'],
#                             "HSNCode":b['HSNCode'],
#                             "Discount":b['Discount'],
#                             "DiscountAmount":b['DiscountAmount']
#                         })    
                    
#                     InvoiceSerializedata = InvoiceSerializerSecond(InvoiceQuery, many=True).data
#                     InvoiceData = list()
#                     for a in InvoiceSerializedata:
#                         InvoiceReferenceDetails = list()
#                         for d in a['InvoicesReferences']:
#                             InvoiceReferenceDetails.append({
#                                 # "Invoice": d['Invoice'],
#                                 "Order": d['Order']['id'],
#                                 "FullOrderNumber": d['Order']['FullOrderNumber'],
#                             })
                            
#                         DefCustomerAddress = ''  
#                         for ad in a['Customer']['PartyAddress']:
#                             if ad['IsDefault'] == True :
#                                 DefCustomerAddress = ad['Address']
                                
#                         DefPartyAddress = ''
#                         for x in a['Party']['PartyAddress']:
#                             if x['IsDefault'] == True :
#                                 DefPartyAddress = x['Address']
                    
#                         InvoiceData.append({
#                             "id": a['id'],
#                             "InvoiceDate": a['InvoiceDate'],
#                             "InvoiceNumber": a['InvoiceNumber'],
#                             "FullInvoiceNumber": a['FullInvoiceNumber'],
#                             "GrandTotal": a['GrandTotal'],
#                             "RoundOffAmount":a['RoundOffAmount'],
#                             "Customer": a['Customer']['id'],
#                             "CustomerName": a['Customer']['Name'],
#                             "CustomerGSTIN": a['Customer']['GSTIN'],
#                             "Party": a['Party']['id'],
#                             "PartyName": a['Party']['Name'],
#                             "PartyGSTIN": a['Party']['GSTIN'],
#                             "PartyFSSAINo": a['Party']['PartyAddress'][0]['FSSAINo'],
#                             "CustomerFSSAINo": a['Customer']['PartyAddress'][0]['FSSAINo'],
#                             "PartyState": a['Party']['State']['Name'],
#                             "CustomerState": a['Customer']['State']['Name'],
#                             "PartyAddress": DefPartyAddress,                            
#                             "CustomerAddress": DefCustomerAddress,
#                             "DriverName":a['Driver']['Name'],
#                             "VehicleNo": a['Vehicle']['VehicleNumber'],
#                             "CreatedOn" : a['CreatedOn'],
#                             "InvoiceItems": InvoiceItemDetails,
#                             "InvoicesReferences": InvoiceReferenceDetails,                              
#                         })
#                     return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': InvoiceData[0]})
#                 return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Invoice Data Not available ', 'Data': []})
#         except Exception as e:
#             return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})    
    

    def get(self, request, id=0):
        try:
            with transaction.atomic():
                InvoiceQuery = T_Invoices.objects.filter(id=id)
                if InvoiceQuery.exists():
                    InvoiceSerializedata = InvoiceSerializerSecond(InvoiceQuery, many=True).data
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': InvoiceSerializedata})
                    InvoiceData = list()
                    for a in InvoiceSerializedata:
                        InvoiceItemDetails = list()
                        for b in a['InvoiceItems']:
                            aaaa=UnitwiseQuantityConversion(b['Item']['id'],b['Quantity'],b['Unit']['id'],0,0,0,0).GetConvertingBaseUnitQtyBaseUnitName()
                            if (aaaa == b['Unit']['UnitID']['Name']):
                                bb=""
                            else:
                                bb=aaaa   
                                
                            InvoiceItemDetails.append({
                                "Item": b['Item']['id'],
                                "ItemName": b['Item']['Name'],
                                "Quantity": b['Quantity'],
                                "MRP": b['MRP']['id'],
                                "MRPValue": b['MRPValue'],
                                "Rate": b['Rate'],
                                "TaxType": b['TaxType'],
                                "PrimaryUnitName":b['Unit']['UnitID']['Name'],
                                "UnitName":bb,
                                "BaseUnitQuantity": b['BaseUnitQuantity'],
                                "GST": b['GST']['id'],
                                "GSTPercentage": b['GSTPercentage'],
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
                                "HSNCode":b['GST']['HSNCode'],
                                "DiscountType":b['DiscountType'],
                                "Discount":b['Discount'],
                                "DiscountAmount":b['DiscountAmount']
                            })
                            
                            InvoiceReferenceDetails = list()
                            for d in a['InvoicesReferences']:
                                
                                
                                InvoiceReferenceDetails.append({
                                    # "Invoice": d['Invoice'],
                                    "Order": d['Order']['id'],
                                    "FullOrderNumber": d['Order']['FullOrderNumber'],
                                    "Description":d['Order']['Description']
                                })
                            
                        DefCustomerAddress = ''  
                        for ad in a['Customer']['PartyAddress']:
                            if ad['IsDefault'] == True :
                                DefCustomerAddress = ad['Address']
                                
                        DefPartyAddress = ''
                        for x in a['Party']['PartyAddress']:
                            if x['IsDefault'] == True :
                                DefPartyAddress = x['Address']

                        # code by ankita 
                        # DefCustomerRoute = ''
                        # for bb in a['Customer']['MCSubParty']:
                        #     # if bb['IsDefault'] == True:
                        #         DefCustomerRoute = bb['Route']['Name']
                        
                        
                        query= MC_PartyBanks.objects.filter(Party=a['Party']['id'],IsSelfDepositoryBank=1,IsDefault=1).all()
                        BanksSerializer=PartyBanksSerializer(query, many=True).data
                        BankData=list()
                        for e in BanksSerializer:
                            if e['IsDefault'] == 1:
                                BankData.append({
                                    "BankName": e['BankName'],
                                    "BranchName": e['BranchName'],
                                    "IFSC": e['IFSC'],
                                    "AccountNo": e['AccountNo'],
                                    "IsDefault" : e['IsDefault']
                                })
                            
                        InvoiceData.append({
                            "id": a['id'],
                            "InvoiceDate": a['InvoiceDate'],
                            "InvoiceNumber": a['InvoiceNumber'],
                            "FullInvoiceNumber": a['FullInvoiceNumber'],
                            "TCSAmount" : a["TCSAmount"], 
                            "GrandTotal": a['GrandTotal'],
                            "RoundOffAmount":a['RoundOffAmount'],
                            "Customer": a['Customer']['id'],
                            "CustomerName": a['Customer']['Name'],
                            "CustomerGSTIN": a['Customer']['GSTIN'],
                            "CustomerMobileNo": a['Customer']['MobileNo'],
                            "Party": a['Party']['id'],
                            "PartyName": a['Party']['Name'],
                            "PartyGSTIN": a['Party']['GSTIN'],
                            "PartyMobileNo": a['Party']['MobileNo'],
                            "PartyFSSAINo": a['Party']['PartyAddress'][0]['FSSAINo'],
                            "CustomerFSSAINo": a['Customer']['PartyAddress'][0]['FSSAINo'],
                            "PartyState": a['Party']['State']['Name'],
                            "CustomerState": a['Customer']['State']['Name'],
                            "PartyAddress": DefPartyAddress,                            
                            "CustomerAddress": DefCustomerAddress,
                            # "CustomerRoute":DefCustomerRoute,
                            "DriverName":a['Driver']['Name'],
                            "VehicleNo": a['Vehicle']['VehicleNumber'],
                            "CreatedOn" : a['CreatedOn'],
                            "InvoiceItems": InvoiceItemDetails,
                            "InvoicesReferences": InvoiceReferenceDetails,
                            "InvoiceUploads" : a["InvoiceUploads"],
                            "BankData":BankData
                                                        
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': InvoiceData[0]})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Invoice Data Not available ', 'Data': []})
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
        except IntegrityError:
            return JsonResponse({'StatusCode': 226, 'Status': True, 'Message': 'This Transaction used in another table', 'Data': []})
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
                                "MRPValue": b['MRPValue'],
                                "Rate": b['Rate'],
                                "TaxType": b['TaxType'],
                                "Unit": b['Unit']['id'],
                                "UnitName": b['Unit']['BaseUnitConversion'],
                                "BaseUnitQuantity": b['BaseUnitQuantity'],
                                "GST": b['GST']['id'],
                                "GSTPercentage": b['GSTPercentage'],
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
                                "DiscountType": b['DiscountType'],
                                "Discount": b['Discount'],
                                "DiscountAmount": b['DiscountAmount'],
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
                for aa in Invoicedata['BulkData']:
                    CustomerMapping=M_PartyCustomerMappingMaster.objects.filter(MapCustomer=aa['Customer'],Party=aa['Party']).values("Customer")
                   
                    if CustomerMapping.count() > 0:
                        aa['Customer']=CustomerMapping[0]['Customer']
                    else:
                        return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': " Customer Data Mapping Missing", 'Data':[]})    
                    # print(aa['Customer'])
                    for bb in aa['InvoiceItems']:
                        ItemMapping=M_ItemMappingMaster.objects.filter(MapItem=bb['Item'],Party=aa['Party']).values("Item")
                        if ItemMapping.count() > 0:
                            bb['Item']=ItemMapping[0]['Item']
                        else:
                            return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': " Item Data Mapping Missing", 'Data':[]})     
                        UnitMapping=M_UnitMappingMaster.objects.filter(MapUnit=bb['Unit'],Party=aa['Party']).values("Unit")
                        if UnitMapping.count() > 0:
                            MC_UnitID=MC_ItemUnits.objects.filter(UnitID=UnitMapping[0]["Unit"],Item=ItemMapping[0]["Item"],IsDeleted=0).values("id")
                            if MC_UnitID.count() > 0:
                                bb['Unit']=MC_UnitID[0]['id']
                            else:
                                return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': " MC_ItemUnits Data Mapping Missing", 'Data':[]})            
                        else:
                            return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': " Unit Data Mapping Missing", 'Data':[]})
                    Invoice_serializer = BulkInvoiceSerializer(data=aa)
                    if Invoice_serializer.is_valid():
                        Invoice_serializer.save()
                    else:
                        transaction.set_rollback(True)
                        return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': Invoice_serializer.errors, 'Data': []})
                return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'Invoice Save Successfully', 'Data':[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': e, 'Data': []})