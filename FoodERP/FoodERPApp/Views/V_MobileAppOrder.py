import base64
from http.client import responses
from urllib import response
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from rest_framework.parsers import JSONParser
from ..Views.V_TransactionNumberfun import GetMaxNumber, GetPrifix
from ..Views.V_CommFunction import *
from ..Serializer.S_Orders import *
from ..Serializer.S_MobileAppOrder import *
from ..models import *
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.authentication import BasicAuthentication
import json ,requests

class T_MobileAppOrdersView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [BasicAuthentication]


    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                data = JSONParser().parse(request)
                auth_header = request.META.get('HTTP_AUTHORIZATION')
                print(auth_header)
                if auth_header:
                    print('000000000')
                    # Parsing the authorization header
                    auth_type, auth_string = auth_header.split(' ', 1)
                    if auth_type.lower() == 'basic':
                        print('000011111')
                        # Decoding the base64-encoded username and password
                        try:
                            username, password = base64.b64decode(
                                auth_string).decode().split(':', 1)
                        except (TypeError, ValueError, UnicodeDecodeError):
                            return responses('Invalid authorization header', status=status.HTTP_401_UNAUTHORIZED)
                        # Authenticating the user
                    print(username,password)    
                    print('1111!1')    
                    user = authenticate(request, username=username, password=password)
                    print(username,password)
                    InvoiceItems = list()
                    
                    if user is not None:
                        print('aaaaaaaaaaaa')
                        Supplier = data['FoodERPSupplierID']
                        Customer = data['FoodERPRetailerID']
                        OrderDate = data['OrderDate']
                        OrderAmount = data['TotalOrderValue']
                        AppOrderNumber = data['AppOrderNumber']
                        Orderdata = list()

                        Orderitem=list()
                        
                        for aa in data['OrderItem']:
                            print(aa['FoodERPItemID'])
                            unit=MC_ItemUnits.objects.filter(UnitID_id=1,Item_id=aa['FoodERPItemID'],IsDeleted=0).values('id')
                            Gst = GSTHsnCodeMaster(aa['FoodERPItemID'], OrderDate).GetTodaysGstHsnCode()
                            BasicAmount=round(float(aa['RatewithoutGST'])*float(aa['QuantityinPieces']),2)
                            CGST= round(BasicAmount*(float(Gst[0]['GST'])/100),2)
                            BaseUnitQuantity = UnitwiseQuantityConversion(
                                aa['FoodERPItemID'], aa['QuantityinPieces'], unit[0]['id'], 0, 0, 0, 0).GetBaseUnitQuantity()
                            QtyInNo = UnitwiseQuantityConversion(
                                aa['FoodERPItemID'], aa['QuantityinPieces'], unit[0]['id'], 0, 0, 1, 0).ConvertintoSelectedUnit()
                            QtyInKg = UnitwiseQuantityConversion(
                                aa['FoodERPItemID'], aa['QuantityinPieces'], unit[0]['id'], 0, 0, 2, 0).ConvertintoSelectedUnit()
                            QtyInBox = UnitwiseQuantityConversion(
                                aa['FoodERPItemID'], aa['QuantityinPieces'], unit[0]['id'], 0, 0, 4, 0).ConvertintoSelectedUnit()
                        
                            
                            
                            Orderitem.append(
                                {
                                    "Item": aa['FoodERPItemID'],
                                    "Quantity": aa['QuantityinPieces'],
                                    "MRP": '',
                                    "MRPValue": aa['MRP'],
                                    "Rate": aa['RatewithoutGST'],
                                    "Unit": unit[0]['id'],
                                    "BaseUnitQuantity": BaseUnitQuantity,
                                    "Margin": "",
                                    "GST": Gst[0]['Gstid'],
                                    "CGST": CGST,
                                    "SGST": CGST,
                                    "IGST": 0,
                                    "GSTPercentage": float(Gst[0]['GST']),
                                    "CGSTPercentage": float(Gst[0]['GST'])/2,
                                    "SGSTPercentage": float(Gst[0]['GST'])/2,
                                    "IGSTPercentage": "0.00",
                                    "BasicAmount": BasicAmount,
                                    "GSTAmount": round(CGST+CGST,2),
                                    "Amount": round(BasicAmount+CGST+CGST,2),
                                    "TaxType": "GST",
                                    "DiscountType": "2",
                                    "Discount": 0,
                                    "DiscountAmount": "0.00",
                                    "IsDeleted": 0,
                                    "Comment": '',
                                    "QtyInNo" : QtyInNo,
                                    "QtyInKg" : QtyInKg,
                                    "QtyInBox" : QtyInBox


                                    }
                            )
                            
                        '''Get Max Order Number'''
                        a = GetMaxNumber.GetOrderNumber(Supplier, 2, OrderDate)
                        '''Get Order Prifix '''
                        b = GetPrifix.GetOrderPrifix(Supplier)
                        
                        c=MC_PartyAddress.objects.filter(Party_id=Customer,IsDefault=1).values('id')
                        print(c)
                            
                        
                        Orderdata.append({
                            
                            "OrderDate": OrderDate,
                            "DeliveryDate": OrderDate,
                            "OrderAmount": OrderAmount,
                            "Description": "",
                            "BillingAddress": c[0]['id'],
                            "ShippingAddress": c[0]['id'],
                            "OrderNo": a,
                            # "FullOrderNumber": b+""+str(a),
                            "FullOrderNumber" : AppOrderNumber,
                            "Division": Supplier,
                            "POType": 1,
                            "POFromDate": OrderDate,
                            "POToDate": OrderDate,
                            "CreatedBy": 1,
                            "UpdatedBy": 1,
                            "OrderTermsAndConditions": [
                                {
                                "TermsAndCondition": 1,
                                "IsDeleted": 0
                                }
                            ],
                            "Customer": Customer,
                            "Supplier": Supplier,
                            "OrderType": 2,
                            "IsConfirm": True,
                            "OrderItem" :  Orderitem

                        })

                        # return JsonResponse({ 'Data': Orderdata })
                        Order_serializer = T_OrderSerializer(data=Orderdata[0])
                        if Order_serializer.is_valid():
                            Order_serializer.save()
                            OrderID = Order_serializer.data['id']
                            PartyID = Order_serializer.data['Customer']
                            

                            log_entry = create_transaction_log(request, Orderdata, 0, Supplier, 'MobileAppOrder Save Successfully',149,OrderID)    
                            return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'Order Save Successfully', 'FoodERPOrderID': OrderID})
                        log_entry = create_transaction_log(request, Orderdata, 0, 0, Order_serializer.errors,161,0)
                        return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': Order_serializer.errors, 'Data': []})
                    else:
                        print('bbbbbbbbbb')
                        # Invalid authorization header or authentication failed
                        return response('Unauthorized', status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            # log_entry = create_transaction_log(request, Orderdata, 0, 0, Exception(e),33,0)
            print('ccccccccccccccccccc')
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  e, 'Data': []})



    @transaction.atomic()
    def put(self, request,id=0):
        try:
            with transaction.atomic():
                data = JSONParser().parse(request)
                auth_header = request.META.get('HTTP_AUTHORIZATION')
                print(auth_header)
                if auth_header:
                    print('000000000')
                    # Parsing the authorization header
                    auth_type, auth_string = auth_header.split(' ', 1)
                    if auth_type.lower() == 'basic':
                        print('000011111')
                        # Decoding the base64-encoded username and password
                        try:
                            username, password = base64.b64decode(
                                auth_string).decode().split(':', 1)
                        except (TypeError, ValueError, UnicodeDecodeError):
                            return responses('Invalid authorization header', status=status.HTTP_401_UNAUTHORIZED)
                        # Authenticating the user
                    print(username,password)    
                    print('1111!1')    
                    user = authenticate(request, username=username, password=password)
                    print(username,password)
                    InvoiceItems = list()
                    
                    if user is not None:
                        print('aaaaaaaaaaaa')
                        print(id)
                        OrderupdateByID = T_Orders.objects.get(id=id)
                        print(OrderupdateByID)
                        Supplier = data['FoodERPSupplierID']
                        Customer = data['FoodERPRetailerID']
                        OrderDate = data['OrderDate']
                        OrderAmount = data['TotalOrderValue']
                        AppOrderNumber = data['AppOrderNumber']
                        Orderdata = list()

                        Orderitem=list()
                        
                        for aa in data['OrderItem']:
                            print(aa['FoodERPItemID'])
                            unit=MC_ItemUnits.objects.filter(UnitID_id=1,Item_id=aa['FoodERPItemID'],IsDeleted=0).values('id')
                            Gst = GSTHsnCodeMaster(aa['FoodERPItemID'], OrderDate).GetTodaysGstHsnCode()
                            BasicAmount=round(float(aa['RatewithoutGST'])*float(aa['QuantityinPieces']),2)
                            CGST= round(BasicAmount*(float(Gst[0]['GST'])/100),2)
                            BaseUnitQuantity = UnitwiseQuantityConversion(
                                aa['FoodERPItemID'], aa['QuantityinPieces'], unit[0]['id'], 0, 0, 0, 0).GetBaseUnitQuantity()
                            QtyInNo = UnitwiseQuantityConversion(
                                aa['FoodERPItemID'], aa['QuantityinPieces'], unit[0]['id'], 0, 0, 1, 0).ConvertintoSelectedUnit()
                            QtyInKg = UnitwiseQuantityConversion(
                                aa['FoodERPItemID'], aa['QuantityinPieces'], unit[0]['id'], 0, 0, 2, 0).ConvertintoSelectedUnit()
                            QtyInBox = UnitwiseQuantityConversion(
                                aa['FoodERPItemID'], aa['QuantityinPieces'], unit[0]['id'], 0, 0, 4, 0).ConvertintoSelectedUnit()
                        
                            
                            
                            Orderitem.append(
                                {
                                    "Item": aa['FoodERPItemID'],
                                    "Quantity": aa['QuantityinPieces'],
                                    "MRP": '',
                                    "MRPValue": aa['MRP'],
                                    "Rate": aa['RatewithoutGST'],
                                    "Unit": unit[0]['id'],
                                    "BaseUnitQuantity": BaseUnitQuantity,
                                    "Margin": "",
                                    "GST": Gst[0]['Gstid'],
                                    "CGST": CGST,
                                    "SGST": CGST,
                                    "IGST": 0,
                                    "GSTPercentage": float(Gst[0]['GST']),
                                    "CGSTPercentage": float(Gst[0]['GST'])/2,
                                    "SGSTPercentage": float(Gst[0]['GST'])/2,
                                    "IGSTPercentage": "0.00",
                                    "BasicAmount": BasicAmount,
                                    "GSTAmount": round(CGST+CGST,2),
                                    "Amount": round(BasicAmount+CGST+CGST,2),
                                    "TaxType": "GST",
                                    "DiscountType": "2",
                                    "Discount": 0,
                                    "DiscountAmount": "0.00",
                                    "IsDeleted": 1,
                                    "Comment": '',
                                    "QtyInNo" : QtyInNo,
                                    "QtyInKg" : QtyInKg,
                                    "QtyInBox" : QtyInBox


                                    }
                            )
                            
                        '''Get Max Order Number'''
                        a = GetMaxNumber.GetOrderNumber(Supplier, 2, OrderDate)
                        '''Get Order Prifix '''
                        # b = GetPrifix.GetOrderPrifix(Supplier)
                        
                        c=MC_PartyAddress.objects.filter(Party_id=Customer,IsDefault=1).values('id')
                        print(c)
                            
                        
                        Orderdata.append({
                            
                            "OrderDate": OrderDate,
                            "DeliveryDate": OrderDate,
                            "OrderAmount": OrderAmount,
                            "Description": "",
                            "BillingAddress": c[0]['id'],
                            "ShippingAddress": c[0]['id'],
                            "OrderNo": a,
                            # "FullOrderNumber": b+""+str(a),
                            "FullOrderNumber" : AppOrderNumber,
                            "Division": Supplier,
                            "POType": 1,
                            "POFromDate": OrderDate,
                            "POToDate": OrderDate,
                            "CreatedBy": 1,
                            "UpdatedBy": 1,
                            "OrderTermsAndConditions": [
                                {
                                "TermsAndCondition": 1,
                                "IsDeleted": 0
                                }
                            ],
                            "Customer": Customer,
                            "Supplier": Supplier,
                            "OrderType": 2,
                            "IsConfirm": True,
                            "OrderItem" :  Orderitem

                        })
                        
                        # return JsonResponse({ 'Data': Orderdata })
                        Order_serializer = T_OrderSerializer(
                    OrderupdateByID, data=Orderdata[0])
                        # Order_serializer = T_OrderSerializer(data=Orderdata[0])
                        if Order_serializer.is_valid():
                            Order_serializer.save()
                            OrderID = Order_serializer.data['id']
                            PartyID = Order_serializer.data['Customer']
                            

                            log_entry = create_transaction_log(request, Orderdata, 0, Supplier, 'MobileAppOrder Update Successfully',150,OrderID)    
                            return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'Order Update Successfully', 'FoodERPOrderID': OrderID})
                        log_entry = create_transaction_log(request, Orderdata, 0, 0, Order_serializer.errors,162,0)
                        return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': Order_serializer.errors, 'Data': []})
                    else:
                        print('bbbbbbbbbb')
                        # Invalid authorization header or authentication failed
                        return response('Unauthorized', status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            # log_entry = create_transaction_log(request, Orderdata, 0, 0, Exception(e),33,0)
            print('ccccccccccccccccccc')
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  e, 'Data': []})

class T_MobileAppOrdersDeleteView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [BasicAuthentication]

    @transaction.atomic()
    def post(self, request, id=0):
        try:
            with transaction.atomic():
                data = JSONParser().parse(request)
                auth_header = request.META.get('HTTP_AUTHORIZATION')
                print(auth_header)
                if auth_header:
                    print('000000000')
                    # Parsing the authorization header
                    auth_type, auth_string = auth_header.split(' ', 1)
                    if auth_type.lower() == 'basic':
                        print('000011111')
                        # Decoding the base64-encoded username and password
                        try:
                            username, password = base64.b64decode(
                                auth_string).decode().split(':', 1)
                        except (TypeError, ValueError, UnicodeDecodeError):
                            return responses('Invalid authorization header', status=status.HTTP_401_UNAUTHORIZED)
                        # Authenticating the user
                    print(username,password)    
                    print('1111!1')    
                    user = authenticate(request, username=username, password=password)
                    print(username,password)
                    InvoiceItems = list()
                    
                    if user is not None:
                        id = data['FoodERPOrderID']
                        Order_Data = T_Orders.objects.get(id=id)
                        Order_Data.delete()
                        log_entry = create_transaction_log(request, {'OrderID':id}, 0, 0,'MobileAPPOrder Deleted Successfully',151,0)
                        return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Order Deleted Successfully'})
        except T_Orders.DoesNotExist:
            log_entry = create_transaction_log(request, {'OrderID':id}, 0, 0,'Record Not available',163,0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Record Not available', 'Data': []})
        except IntegrityError:
            log_entry = create_transaction_log(request, {'OrderID':id}, 0,0, 'This Order is used in another Transaction ',163,0)
            return JsonResponse({'StatusCode': 226, 'Status': True, 'Message': 'This Order is used in another Transaction'})
        except Exception as e:
            log_entry = create_transaction_log(request, {'OrderID':id}, 0, 0,Exception(e),163,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

class NewProductSendToMobileAppView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic()
    def post(self, request,id=0):
        try:
            with transaction.atomic():
                
                ItemData=list()
                today = date.today()
                q0=M_Items.objects.raw('''SELECT M_Items.id ,M_Items.Name ItemName,ifnull(M_GroupType.Name,'') GroupTypeName,ifnull(M_Group.Name,'') FoodERPParentName,ifnull(MC_SubGroup.Name,'') FoodERPFamilyName 
,ifnull(MC_ItemGroupDetails.GroupType_id,'') GroupTypeId,ifnull(MC_ItemGroupDetails.Group_id,'') FoodERPParentId,ifnull(MC_ItemGroupDetails.SubGroup_id,'') FoodERPFamilyId,M_Items.BaseUnitID_id,M_Items.isActive
,GSTHsnCodeMaster(M_Items.id,%s,3) HSNCode,GetTodaysDateMRP(M_Items.id,%s,2,0,0) MRPValue
FROM M_Items
left join MC_ItemGroupDetails on MC_ItemGroupDetails.Item_id=M_Items.id
left JOIN M_GroupType ON M_GroupType.id = MC_ItemGroupDetails.GroupType_id 
left JOIN M_Group ON M_Group.id  = MC_ItemGroupDetails.Group_id 
left JOIN MC_SubGroup ON MC_SubGroup.id  = MC_ItemGroupDetails.SubGroup_id
where M_Items.id=%s''',([today],[today],[id]))
                print(q0)
                for row in q0:
                     
                    RetaileRate=RateCalculationFunction(0,row.id,0,0,1,0,3).RateWithGST() 
                    DistributorRate=RateCalculationFunction(0,row.id,0,0,1,0,2).RateWithGST()
                    SuperStockistRate=RateCalculationFunction(0,row.id,0,0,1,0,1).RateWithGST()
                    if row.isActive == True:
                        ss='true'
                    else:
                        ss='false'    
                    ItemData.append({
                            "FoodERPItemID": str(row.id),
                            "FoodERPCategoryId":1,
                            "FoodERPFamilyId":int(row.FoodERPFamilyId),
                            "FoodERPTypeId":1,
                            "FoodERPUomId":row.BaseUnitID_id,
                            "ItemName":row.ItemName,
                            "MRP":float(row.MRPValue),
                            "RetailerRate":float(RetaileRate[0]['RateWithoutGST']),
                            "DistributorRate":float(DistributorRate[0]['RateWithoutGST']),
                            "SuperStockistRate":float(SuperStockistRate[0]['RateWithoutGST']),
                            "ProductHSN":row.HSNCode,
                            "IsActive":bool(ss)
                            
                        })

                payload={
                    "products" : ItemData
                }
                url = "http://webapp.theskygge.com/fmcg_middleware/products/add"

                headers = {
                            'SecureToken': '1AJ6IseHBRn+fMD2cRmvMfZYXTUY/qGiX1qfGeOGV8nNa7LJH6osRq9ga3uGgU2P4gsvR/GGp5KQcNII7qdBjN/mt/DVo8nnWMNqzoRFDBiQXzK4k/yE7rlMCDgz42Y7',
                            'Content-Type': 'application/json'
                          }
                
                
                payload_json_data = json.dumps(payload)
                
                response = requests.request("POST", url, headers=headers, data=payload_json_data)
                
                response_json=json.loads(response.text)
                print(response_json)
                print('==============================',response_json['success'])
                if(response_json['success'] == True):
                    log_entry = create_transaction_log(request, payload_json_data, 0, 0,response_json,152)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':response_json['message'], 'Data': []})
                else:
                    log_entry = create_transaction_log(request, payload_json_data, 0, 0,response_json['message'],164)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':response_json, 'Data': []})
        except Exception as e:
            # log_entry = create_transaction_log(request, payload_json_data, 0, 0,response_json,164)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})            
        
    @transaction.atomic()
    def put(self, request,id=0):
        try:
            with transaction.atomic():
                # data = JSONParser().parse(request)
                # log_entry = create_transaction_log(request, data, 0, 0, "initiat")
                # payload = json.dumps(data)
                ItemData=list()
                today = date.today()
                q0=M_Items.objects.raw('''SELECT M_Items.id ,M_Items.Name ItemName,ifnull(M_GroupType.Name,'') GroupTypeName,ifnull(M_Group.Name,'') FoodERPParentName,ifnull(MC_SubGroup.Name,'') FoodERPFamilyName 
,ifnull(MC_ItemGroupDetails.GroupType_id,'') GroupTypeId,ifnull(MC_ItemGroupDetails.Group_id,'') FoodERPParentId,ifnull(MC_ItemGroupDetails.SubGroup_id,'') FoodERPFamilyId,M_Items.BaseUnitID_id,M_Items.isActive
,GSTHsnCodeMaster(M_Items.id,%s,3) HSNCode,GetTodaysDateMRP(M_Items.id,%s,2,0,0) MRPValue
FROM M_Items
left join MC_ItemGroupDetails on MC_ItemGroupDetails.Item_id=M_Items.id
left JOIN M_GroupType ON M_GroupType.id = MC_ItemGroupDetails.GroupType_id 
left JOIN M_Group ON M_Group.id  = MC_ItemGroupDetails.Group_id 
left JOIN MC_SubGroup ON MC_SubGroup.id  = MC_ItemGroupDetails.SubGroup_id
where M_Items.id=%s''',([today],[today],[id]))
                print(q0)
                for row in q0:
                    RetaileRate=RateCalculationFunction(0,row.id,0,0,1,0,3).RateWithGST() 
                    DistributorRate=RateCalculationFunction(0,row.id,0,0,1,0,2).RateWithGST()
                    SuperStockistRate=RateCalculationFunction(0,row.id,0,0,1,0,1).RateWithGST() 
                    ItemData.append({
                            "FoodERPItemID": str(row.id),
                            "FoodERPCategoryId":1,
                            "FoodERPFamilyId":row.FoodERPFamilyId,
                            "FoodERPTypeId":1,
                            "FoodERPUomId":row.BaseUnitID_id,
                            "ItemName":row.ItemName,
                            "MRP":float(row.MRPValue),
                            "RetailerRate":float(RetaileRate[0]['RateWithoutGST']),
                            "DistributorRate":float(DistributorRate[0]['RateWithoutGST']),
                            "SuperStockistRate":float(SuperStockistRate[0]['RateWithoutGST']),
                            "ProductHSN":row.HSNCode,
                            "IsActive":row.isActive
                            
                        })

                payload={
                    "products" : ItemData
                }
                url = "http://webapp.theskygge.com/fmcg_middleware/products/update"

                headers = {
                            'SecureToken': '1AJ6IseHBRn+fMD2cRmvMfZYXTUY/qGiX1qfGeOGV8nNa7LJH6osRq9ga3uGgU2P4gsvR/GGp5KQcNII7qdBjN/mt/DVo8nnWMNqzoRFDBiQXzK4k/yE7rlMCDgz42Y7',
                            'Content-Type': 'application/json'
                          }
                
                payload_json_data = json.dumps(payload)
                response = requests.request("put", url, headers=headers, data=payload_json_data)
                response_json=json.loads(response.text)
                
                if(response_json['success'] == True):
                    log_entry = create_transaction_log(request, payload_json_data, 0, 0,response_json['message'],153)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':response_json, 'Data': []})
                else:
                    print('aaaaaaaaaaaaaaaaa')
                    log_entry = create_transaction_log(request, payload_json_data, 0, 0,response_json['message'],165)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':response_json, 'Data': []})

        except Exception as e:
            # log_entry = create_transaction_log(request, payload_json_data, 0, 0,response_json,165)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})                
        
    @transaction.atomic()
    def delete(self, request,id=0):
        try:
            with transaction.atomic():
                
                ItemData=list()
                
                ItemData.append({
                        "FoodERPItemID": id,
                    })

                payload={
                    "products" : ItemData
                }
                url = "http://webapp.theskygge.com/fmcg_middleware/products/delete"

                headers = {
                            'SecureToken': '1AJ6IseHBRn+fMD2cRmvMfZYXTUY/qGiX1qfGeOGV8nNa7LJH6osRq9ga3uGgU2P4gsvR/GGp5KQcNII7qdBjN/mt/DVo8nnWMNqzoRFDBiQXzK4k/yE7rlMCDgz42Y7',
                            'Content-Type': 'application/json'
                          }
                
                payload_json_data = json.dumps(payload)
                response = requests.request("delete", url, headers=headers, data=payload)
                print(response.text)
                
                response_json=json.loads(response.text)
                if(response_json['success'] == True):
                    log_entry = create_transaction_log(request, payload, 0, 0,response_json,154)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':response_json, 'Data': []})
                else:
                    log_entry = create_transaction_log(request, payload, 0, 0,response_json,166)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':response_json, 'Data': []})     
            
        except Exception as e:
            log_entry = create_transaction_log(request, payload, 0, 0,response_json,166)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})    
        
class NewRetailerSendToMobileAppView(CreateAPIView):
    permission_classes = (IsAuthenticated,)        

    @transaction.atomic()
    def post(self, request,id=0):
        try:
            with transaction.atomic():
                
                RetailerData=list()
                today = date.today()
                q0=M_Parties.objects.raw('''SELECT cust.id,cust.Name RetailerName,(cust.MobileNo) MobileNumber,cust.Email EmailAddress,cust.PAN PANNumber,
cust.GSTIN GSTNumber,cust.Latitude, cust.Longitude,dist.id distid,MC_PartyAddress.FSSAINo,MC_PartyAddress.FSSAIExipry,
(select Route_id from MC_PartySubParty where Party_id=dist.id and SubParty_id=cust.id )Route_id,MC_PartyAddress.Address
 FROM MC_PartySubParty 
 join M_Parties dist on dist.id=MC_PartySubParty.Party_id
 join M_Parties cust on cust.id=MC_PartySubParty.SubParty_id
 left join MC_PartyAddress on cust.id = MC_PartyAddress.Party_id and MC_PartyAddress.IsDefault=0
 where cust.PartyType_id=11 and cust.id=%s''',([id]))
                
                for row in q0:
                     
                    RetailerData.append({
                            "FoodERPRetailerID": str(row.id),
                            # "RouteId"       :row.Route_id,
                            "RouteId" : 1,
                            "RetailerName"  :row.RetailerName,
                            "DistributorID" :row.distid,
                            "Address"       :row.Address,
                            "MobileNumber"  :str(row.MobileNumber),
                            "EmailAddress"  :row.EmailAddress,
                            "PANNumber"     :row.PANNumber,
                            "GSTNumber"     :row.GSTNumber,
                            "FSSAINumber"   :row.FSSAINo,
                            "FSSAIExpiry"   :row.FSSAIExipry,
                            # "Latitude"      :row.Latitude,
                            # "Longitude"     :row.Longitude,
                            "IsActive"      :row.isActive
                           
                            
                        })

                payload={
                    "outlets" : RetailerData
                }
                
                url = "http://webapp.theskygge.com/fmcg_middleware/outlets/add"

                headers = {
                            'SecureToken': '1AJ6IseHBRn+fMD2cRmvMfZYXTUY/qGiX1qfGeOGV8nNa7LJH6osRq9ga3uGgU2P4gsvR/GGp5KQcNII7qdBjN/mt/DVo8nnWMNqzoRFDBiQXzK4k/yE7rlMCDgz42Y7',
                            'Content-Type': 'application/json'
                          }
                
                payload_json_data = json.dumps(payload)
                print(payload_json_data)
                response = requests.request(
                    "POST", url, headers=headers, data=payload_json_data)
             
                response_json=json.loads(response.text)
                print(response_json)
                if(response_json['success'] == True):
                    log_entry = create_transaction_log(request, payload_json_data, 0, 0,response_json['message'],155)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':response_json, 'Data': []})
                else:
                    log_entry = create_transaction_log(request, payload_json_data, 0, 0,response_json['message'],167)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':response_json, 'Data': []})

        except Exception as e:
            print("fffffffffffffffddddddddddddddddddddddddddddddddddddddddd",response_json,payload_json_data)
            log_entry = create_transaction_log(request, payload_json_data, 0, 0,response_json,167)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})            
        
    @transaction.atomic()
    def put(self, request,id=0):
        try:
            with transaction.atomic():
                
                RetailerData=list()
                today = date.today()
                q0=M_Parties.objects.raw('''SELECT cust.id,cust.Name RetailerName,cust.MobileNo MobileNumber,cust.Email EmailAddress,cust.PAN PANNumber,
cust.GSTIN GSTNumber,cust.Latitude,cust.Longitude,dist.id distid,MC_PartyAddress.FSSAINo,MC_PartyAddress.FSSAIExipry,
(select Route_id from MC_PartySubParty where Party_id=dist.id and SubParty_id=cust.id )Route_id,MC_PartyAddress.Address
 FROM MC_PartySubParty 
 join M_Parties dist on dist.id=MC_PartySubParty.Party_id
 join M_Parties cust on cust.id=MC_PartySubParty.SubParty_id
 left join MC_PartyAddress on cust.id = MC_PartyAddress.Party_id and MC_PartyAddress.IsDefault=0
 where cust.PartyType_id=11 and cust.id=%s''',([id]))
                print(q0)
                for row in q0:
                    print(row.isActive)
                    RetailerData.append({
                            "FoodERPRetailerID": str(row.id),
                            # "RouteId"       :row.Route_id,
                            "RouteId" : 1,
                            "RetailerName"  :row.RetailerName,
                            "DistributorID" :row.distid,
                            "Address"       :str(row.Address),
                            "MobileNumber"  :str(row.MobileNumber),
                            "EmailAddress"  :str(row.EmailAddress),
                            "PANNumber"     :str(row.PANNumber),
                            "GSTNumber"     :str(row.GSTNumber),
                            "FSSAINumber"   :str(row.FSSAINo),
                            "FSSAIExpiry"   :str(row.FSSAIExipry),
                            "Latitude"      :row.Latitude,
                            "Longitude"     :row.Longitude,
                            "IsActive"      :row.isActive
                           
                            
                        })

                payload={
                    "outlets" : RetailerData
                }
                url = "http://webapp.theskygge.com/fmcg_middleware/outlets/update"

                headers = {
                            'SecureToken': '1AJ6IseHBRn+fMD2cRmvMfZYXTUY/qGiX1qfGeOGV8nNa7LJH6osRq9ga3uGgU2P4gsvR/GGp5KQcNII7qdBjN/mt/DVo8nnWMNqzoRFDBiQXzK4k/yE7rlMCDgz42Y7',
                            'Content-Type': 'application/json'
                          }
                
                payload_json_data = json.dumps(payload)
                print(payload_json_data)
                response = requests.request("put", url, headers=headers, data=payload_json_data)
                response_json=json.loads(response.text)
                print('======================',response_json)
                if(response_json['success'] == True):
                    log_entry = create_transaction_log(request, payload_json_data, 0, 0,response_json['message'],156)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':response_json, 'Data': []})
                else:
                    log_entry = create_transaction_log(request, payload_json_data, 0, 0,response_json['message'],168)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':response_json, 'Data': []})    
            
        except Exception as e:
            # log_entry = create_transaction_log(request, payload_json_data, 0, 0,response_json,168)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})            
            
    @transaction.atomic()
    def delete(self, request,id=0):
        try:
            with transaction.atomic():
                
                RetailerData=list()
                
                RetailerData.append({
                        
                        "FoodERPRetailerID" : id 
                    })

                payload={
                    "outlets" : RetailerData
                }
                url = "http://webapp.theskygge.com/fmcg_middleware/outlets/delete"

                headers = {
                            'SecureToken': '1AJ6IseHBRn+fMD2cRmvMfZYXTUY/qGiX1qfGeOGV8nNa7LJH6osRq9ga3uGgU2P4gsvR/GGp5KQcNII7qdBjN/mt/DVo8nnWMNqzoRFDBiQXzK4k/yE7rlMCDgz42Y7',
                            'Content-Type': 'application/json'
                          }
                
                payload_json_data = json.dumps(payload)
                response = requests.request("delete", url, headers=headers, data=payload_json_data)
                print(response.text)
                response_json=json.loads(response.text)
                
                if(response_json['success'] == True):
                    log_entry = create_transaction_log(request, payload, 0, 0,response_json['message'],157)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':response_json, 'Data': []})
                else:
                    log_entry = create_transaction_log(request, payload, 0, 0,response_json['message'],169)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':response_json, 'Data': []})

        except Exception as e:
            # log_entry = create_transaction_log(request, payload, 0, 0,response_json,169)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})  
        
        
        
class RetailerAddFromMobileAppview(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [BasicAuthentication]
    
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                data = JSONParser().parse(request)
                auth_header = request.META.get('HTTP_AUTHORIZATION')
                if auth_header:
                    # Parsing the authorization header
                    auth_type, auth_string = auth_header.split(' ', 1)
                    if auth_type.lower() == 'basic':
                        # Decoding the base64-encoded username and password
                        try:
                            username, password = base64.b64decode(
                                auth_string).decode().split(':', 1)
                        except (TypeError, ValueError, UnicodeDecodeError):
                            return responses('Invalid authorization header', status=status.HTTP_401_UNAUTHORIZED)
                        # Authenticating the user
                    
                    user = authenticate(request, username=username, password=password)
                    
                    RetailerAddList=list()
                    for a in data['outlets']:
                        query1 = M_Parties.objects.filter(id=a['DistributorId']).values('State_id','District_id','City_id')
                        PartySubParty = list()
                        PartySubParty.append({
                            "Party":a['DistributorId'],
                            "Route": a['RouteId'],
                            "CreatedBy":430,
                            "UpdatedBy":430,  
                        })
                        PartyAddress = list()
                        PartyAddress.append({
                            "Address": a['Address'],
                            "FSSAINo": a['FSSAINumber'],
                            "FSSAIExipry": a['FSSAIExpiry'],
                            "IsDefault": True, 
                        })
                        PartyPrefix = list()
                        PartyPrefix.append({
                            "Orderprefix": "PO",
                            "Invoiceprefix": "IN",
                            "Grnprefix": "GRN",
                            "Receiptprefix": "RE",
                            "WorkOrderprefix": "",
                            "MaterialIssueprefix": "",
                            "Demandprefix": "",
                            "IBChallanprefix": "",
                            "IBInwardprefix": "",
                            "PurchaseReturnprefix": "PR",
                            "Creditprefix": "CR",
                            "Debitprefix": "DR" 
                        })
                        
                        RetailerAddList.append(
                            {
                                "Name":a['RetailerName'],
                                "PriceList": 3,
                                "PartyType": 11,
                                "Company": 3,
                                "PAN": a['PANNumber'],
                                "Email":a['EmailAddress'],
                                "MobileNo": a['MobileNumber'],
                                "Latitude": a['Latitude'],
                                "Longitude": a['Longitude'],
                                "GSTIN": a['GSTNumber'],
                                "isActive": a['IsActive'],
                                "CreatedBy":430,
                                "UpdatedBy":430,
                                "IsApprovedParty":1,
                                "State":query1[0]['State_id'], #Compensary
                                "District":query1[0]['District_id'], #Compensary
                                "City":query1[0]['City_id'], #Compensary
                                "PartySubParty":PartySubParty,
                                "PartyAddress":PartyAddress,
                                "PartyPrefix":PartyPrefix
                            })
                        
                    for aa in RetailerAddList:
                        Retailer_serializer = RetailerAddFromMobileAppSerializer(data=aa)
                        if Retailer_serializer.is_valid():
                            Retailer = Retailer_serializer.save()
                            LastInsertID = Retailer.id
                            
                            log_entry = create_transaction_log(request, aa, 0, 0,'Retailer Added From MobileApp Successfully',158,LastInsertID)
                            return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'Retailer Added From MobileApp Successfully',"FoodERPRetailerID":LastInsertID}) 
                        else:
                            transaction.set_rollback(True)
                            log_entry = create_transaction_log(request, aa, 0, 0,'fail to Added Retailer From MobileApp ',170,0)
                            return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': Retailer_serializer.errors})
                    # return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'Retailer Added From App Successfully',"FoodERPRetailerID":LastInsertID})                        
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  e })
        
        
        
class RetailerUpdateFromMobileAppview(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [BasicAuthentication]
    
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                data = JSONParser().parse(request)
                auth_header = request.META.get('HTTP_AUTHORIZATION')
                if auth_header:
                    # Parsing the authorization header
                    auth_type, auth_string = auth_header.split(' ', 1)
                    if auth_type.lower() == 'basic':
                        # Decoding the base64-encoded username and password
                        try:
                            username, password = base64.b64decode(
                                auth_string).decode().split(':', 1)
                        except (TypeError, ValueError, UnicodeDecodeError):
                            return responses('Invalid authorization header', status=status.HTTP_401_UNAUTHORIZED)
                        # Authenticating the user
                    
                    user = authenticate(request, username=username, password=password)
                    
                    RetailerAddList=list()
                    for a in data['outlets']:
                        
                        PartyAddress = list()
                        PartyAddress.append({
                            "FoodERPRetailerID":a['FoodERPRetailerID'],
                            "Address": a['Address'],
                            "FSSAINo": a['FSSAINumber'],
                            "FSSAIExipry": a['FSSAIExpiry']
                           
                        })
                        RetailerAddList.append(
                            {
                                "FoodERPRetailerID":a['FoodERPRetailerID'],
                                "Name":a['RetailerName'],
                                "PAN": a['PANNumber'],
                                "Email":a['EmailAddress'],
                                "MobileNo": a['MobileNumber'],
                                "Latitude": a['Latitude'],
                                "Longitude": a['Longitude'],
                                "GSTIN": a['GSTNumber'],
                                "isActive": a['IsActive'],
                                "UpdatedBy":430,
                                "PartyAddress":PartyAddress
                            })
                    
                    # return JsonResponse({'StatusCode': 406, 'Status': True,  'Message':RetailerAddList, 'Data': []})    
                    for aa in RetailerAddList:
                        PartiesdataByID = M_Parties.objects.get(id=aa['FoodERPRetailerID'])
                        Retailer_serializer = RetailerUpdateFromMobileAppSerializer(PartiesdataByID, data=aa)
                        if Retailer_serializer.is_valid():
                            Retailer = Retailer_serializer.save()
                            log_entry = create_transaction_log(request, aa, 0, 0,'Retailer Updated From Mobile App Successfully',159)
                            return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'Retailer Updated From Mobile App Successfully' })
                        else:
                            transaction.set_rollback(True)
                            log_entry = create_transaction_log(request, aa, 0, 0,'fail to  Updated retailer From MobileApp ',171)
                            return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': Retailer_serializer.errors})
                    # return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'Retailer Updated From Mobile App Successfully' })                        
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  e, 'Data': []}) 

class RetailerDeleteFromMobileApp(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [BasicAuthentication]
                  
    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                auth_header = request.META.get('HTTP_AUTHORIZATION')
                if auth_header:
                    # Parsing the authorization header
                    auth_type, auth_string = auth_header.split(' ', 1)
                    if auth_type.lower() == 'basic':
                        # Decoding the base64-encoded username and password
                        try:
                            username, password = base64.b64decode(
                                auth_string).decode().split(':', 1)
                        except (TypeError, ValueError, UnicodeDecodeError):
                            return responses('Invalid authorization header', status=status.HTTP_401_UNAUTHORIZED)
                        # Authenticating the user
                    user = authenticate(request, username=username, password=password)
                    M_Partiesdata = M_Parties.objects.get(id=id)
                    M_Partiesdata.delete()
                    log_entry = create_transaction_log(request, id, 0, 0,'Retailer  Deleted Successfully',160)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Retailer  Deleted Successfully'})
        except M_Parties.DoesNotExist:
            log_entry = create_transaction_log(request, id, 0, 0,'Retailer Not available',172)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Retailer Not available'})
        except IntegrityError:
            log_entry = create_transaction_log(request, id, 0, 0,'Retailer used in another table',172)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Retailer used in another table'})              
                 