
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, connection, transaction
from rest_framework.parsers import JSONParser

from ..Serializer.S_Orders import *

from ..Serializer.S_Bom import *

from ..models import *

'''BOM ---   Bill Of Material'''

# class BOMListView(CreateAPIView):
#     permission_classes = (IsAuthenticated,)
#     authentication__Class = JSONWebTokenAuthentication

#     @transaction.atomic()
#     def get(self, request,id=0):
#         try:
#             with transaction.atomic(): 
#                 query = M_BillOfMaterial.objects.all()
#                 if query:
#                     Bom_serializer = M_BOMSerializerSecond(query, many=True).data
#                     BomListData = list()
#                     for a in Bom_serializer:   
#                         BomListData.append({
#                         "id": a['id'],
#                         "BomDate": a['BomDate'],
#                         "Item":a['Item']['id'],
#                         "ItemName": a['Item']['Name'],
#                         "Unit": a['Unit']['id'],
#                         "UnitName": a['Unit']['UnitID']['Name'],
#                         "EstimatedOutputQty" : a['EstimatedOutputQty'],
#                         "Comment": a['Comment'],
#                         "IsActive": a['IsActive'],
#                         "Company": a['Company']['id'],
#                         "CompanyName": a['Company']['Name'],
#                         }) 
#                     return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'','Data': BomListData})
#                 return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'Record Not Found','Data': []})
#         except Exception as e:
#                 return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})


class BOMListFilterView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request,id=0):
        try:
            with transaction.atomic():
                BillOfMaterialdata = JSONParser().parse(request)
                FromDate = BillOfMaterialdata['FromDate']
                ToDate = BillOfMaterialdata['ToDate']
                Company = BillOfMaterialdata['Company']
                query = M_BillOfMaterial.objects.filter(BomDate__range=[FromDate,ToDate],Company_id=Company)
                # return JsonResponse({'query': str(query.query)})
                if query:
                    Bom_serializer = M_BOMSerializerSecond(query, many=True).data
                    BomListData = list()
                    for a in Bom_serializer:
                        Item = a['Item']['id']
                        # obatchwisestockquery = O_BatchWiseLiveStock.objects.filter(Item_id=Item).values('Item').annotate(actualStock=Sum('BaseUnitQuantity')).values('actualStock')
                        obatchwisestockquery=O_BatchWiseLiveStock.objects.raw(''' SELECT O_BatchWiseLiveStock.id,O_BatchWiseLiveStock.Item_id,SUM(O_BatchWiseLiveStock.BaseUnitQuantity) AS actualStock FROM O_BatchWiseLiveStock WHERE O_BatchWiseLiveStock.Item_id = %s GROUP BY O_BatchWiseLiveStock.Item_id''', [Item])
                        if not obatchwisestockquery:
                            StockQty =0.0
                        else:
                            StockQtySerialize_data = StockQtyserializer(obatchwisestockquery, many=True).data
                            StockQty = StockQtySerialize_data[0]['actualStock']   
                        BomListData.append({
                        "id": a['id'],
                        "BomDate": a['BomDate'],
                        "Item":a['Item']['id'],
                        "ItemName": a['Item']['Name'],
                        "Unit": a['Unit']['id'],
                        "UnitName": a['Unit']['UnitID']['Name'],
                        "StockQty":StockQty,
                        "EstimatedOutputQty" : a['EstimatedOutputQty'],
                        "Comment": a['Comment'],
                        "IsActive": a['IsActive'],
                        "Company": a['Company']['id'],
                        "CompanyName": a['Company']['Name'],
                        "CreatedOn" : a['CreatedOn'],
                        }) 
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'','Data': BomListData})
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'Record Not Found','Data': []})
        except Exception as e:
                return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

class M_BOMsView(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                BillOfMaterial = JSONParser().parse(request)
                ReferenceBOMID = BillOfMaterial['ReferenceBom']
                Boms_Serializer = M_BOMSerializer(data=BillOfMaterial)
                if Boms_Serializer.is_valid():
                    Boms_Serializer.save()
                    if(ReferenceBOMID > 0):
                        query = M_BillOfMaterial.objects.filter(id=ReferenceBOMID).update(IsActive=0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Bill Of Material Save Successfully', 'Data': []})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Boms_Serializer.errors, 'Data': []})
        except Exception as e:
                return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})


class M_BOMsViewSecond(RetrieveAPIView):

    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0,Company=0):
        try:
            with transaction.atomic():
                Query = M_BillOfMaterial.objects.filter(id=id,Company_id=Company)
                if Query.exists():
                    BOM_Serializer = M_BOMSerializerSecond(Query,many=True).data
                    BillofmaterialData = list()
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': BOM_Serializer})
                    for a in BOM_Serializer:
                        MaterialDetails =list()
                        ParentItem= a['Item']['id']
                        Parentquery = MC_ItemUnits.objects.filter(Item_id=ParentItem,IsDeleted=0)
                        # print(query.query)
                        if Parentquery.exists():
                            ParentUnitdata = Mc_ItemUnitSerializerThird(Parentquery, many=True).data
                            ParentUnitDetails = list()
                            for d in ParentUnitdata:
                                ParentUnitDetails.append({
                                "Unit": d['id'],
                                "UnitName": d['UnitID']['Name'],
                            })
                        
                        for b in a['BOMItems']:
                            ChildItem= b['Item']['id']
                            query = MC_ItemUnits.objects.filter(Item_id=ChildItem,IsDeleted=0)
                            # print(query.query)
                            if query.exists():
                                Unitdata = Mc_ItemUnitSerializerThird(query, many=True).data
                                UnitDetails = list()
                                for c in Unitdata:
                                    UnitDetails.append({
                                    "Unit": c['id'],
                                    "UnitName": c['UnitID']['Name'],
                                })
                            MaterialDetails.append({
                                "id": b['id'],
                                "Item":b['Item']['id'],
                                "ItemName":b['Item']['Name'], 
                                "Unit": b['Unit']['id'],
                                "UnitName": b['Unit']['UnitID']['Name'],
                                "Quantity":b['Quantity'],
                                "UnitDetails":UnitDetails
                            })
                            
                        BillofmaterialData.append({
                            "id": a['id'],
                            "BomDate": a['BomDate'],
                            "Comment": a['Comment'],
                            "IsActive": a['IsActive'],
                            "Company": a['Company']['id'],
                            "CompanyName":a['Company']['Name'],
                            "Item":a['Item']['id'],
                            "ItemName":a['Item']['Name'],
                            "EstimatedOutputQty": a['EstimatedOutputQty'],  
                            "Unit": a['Unit']['id'],
                            "UnitName": a['Unit']['UnitID']['Name'],
                            "ParentUnitDetails":ParentUnitDetails,
                            "BOMItems":MaterialDetails
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': BillofmaterialData})
        except M_BillOfMaterial.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Bill Of Material Not available', 'Data': []})
       
    @transaction.atomic()
    def put(self, request, id=0, Company=0):
        try:
            with transaction.atomic():
                checkitem = T_WorkOrder.objects.filter(Bom_id=id)
                if checkitem.exists():
                    return JsonResponse({'StatusCode': 100, 'Status': True, 'Message': 'Bill Of Material used in Work Order, Still You Want to Create New Bill Of Material..', 'Data': []})
                else:    
                    Bomsdata = JSONParser().parse(request)
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': Bomsdata })
                    BomsdataByID = M_BillOfMaterial.objects.get(id=id,Company_id=Company)
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': str(BomsdataByID.query)})
                    Boms_Serializer = M_BOMSerializer(BomsdataByID, data=Bomsdata)
                    if Boms_Serializer.is_valid():
                        Boms_Serializer.save()
                        return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Bill Of Material Updated Successfully', 'Data': []})
                    else:
                        transaction.set_rollback(True)
                        return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Boms_Serializer.errors, 'Data': []})    
        except Exception as e:
                return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
    
    @transaction.atomic()
    def delete(self, request, id=0,Company=0):
        try:
            with transaction.atomic():
                Bomsdata = M_BillOfMaterial.objects.get(id=id)
                Bomsdata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Bill Of Material  Deleted Successfully', 'Data': []})
        except M_BillOfMaterial.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Bill Of Material Not available', 'Data': []})
        except IntegrityError:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Bill Of Material used in another table', 'Data': []})
