from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, connection, transaction
from rest_framework.parsers import JSONParser

from ..Serializer.S_PriceLists import *

from ..models import *


def getchildnode(ParentID):
    
    Modulesdata = M_PriceList.objects.filter(BasePriceListID=ParentID)
    cdata=list()
    if Modulesdata.exists():
        Modules_Serializer = PriceListSerializer(Modulesdata, many=True).data
        for z in Modules_Serializer:
        
            cchild=getchildnode(z["id"])
            cdata.append({
                "value":z["id"],
                "label":z["Name"],
                "MkUpMkDn":z["MkUpMkDn"],
                "CalculationPath":z["CalculationPath"],
                "children":cchild
            })
        return cdata
    else:
        return []


class PriceListView(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request):
        try:
            with transaction.atomic():
                query = M_PriceList.objects.all()
                # return JsonResponse({'StatusCode': 204, 'Status': True,'Data':str(query.query)})
                if not query:
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Price List Not available', 'Data': []})
                else:
                    PriceList_Serializer = PriceListSerializerSecond(
                        query, many=True).data
                    PriceListData = list()
                    for a in PriceList_Serializer:
                        PriceListData.append({
                            "id": a['id'],
                            "Name": a['Name'],
                            "BasePriceListID": a['BasePriceListID'],
                            "MkUpMkDn": a['MkUpMkDn'],
                            "PLPartyType": a['PLPartyType']['id'],
                            "PLPartyTypeName": a['PLPartyType']['Name'],
                            "Company":a['Company']['id'],
                            "CompanyName":a['Company']['Name'],
                            "CreatedBy": a['CreatedBy'],
                            "CreatedOn": a['CreatedOn'],
                            "UpdatedBy": a['UpdatedBy'],
                            "UpdatedOn": a['UpdatedOn']
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': PriceListData})
        except Exception as e:
                return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                PriceListdata = JSONParser().parse(request)
                PriceListdata_Serializer = PriceListSerializer(
                    data=PriceListdata)
                if PriceListdata_Serializer.is_valid():
                    PriceListdata_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Price List Save Successfully', 'Data': []})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  PriceListdata_Serializer.errors, 'Data': []})
        except Exception as e:
                return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})


class PriceListViewSecond(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    def get(self, request, id=0):
        try:
            with transaction.atomic():
                query = M_PriceList.objects.filter(PLPartyType_id=id,BasePriceListID=0)
                if not query:
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Price List Not available', 'Data': []})
                else:
                    PriceList_Serializer = PriceListSerializer(query, many=True).data
                    
                    PriceListData = list()
                    for a in PriceList_Serializer:
                        aa=a['id']
                        
                        child=getchildnode(aa)
                        PriceListData.append({ 
                            "value": a['id'],
                            "label": a['Name'],
                            "MkUpMkDn":a["MkUpMkDn"],
                            "CalculationPath":a["CalculationPath"],
                            "children":child
                            })
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': PriceListData})
        except Exception as e:
                return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                PriceListdata = JSONParser().parse(request)
                PriceListdataID = M_PriceList.objects.get(id=id)
                PriceListdata_Serializer = PriceListSerializer(
                    PriceListdataID, data=PriceListdata)
                if PriceListdata_Serializer.is_valid():
                    PriceListdata_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Price List Updated Successfully', 'Data': []})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': PriceListdata_Serializer.errors, 'Data': []})
        except Exception as e:
                return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                PriceListdata = M_PriceList.objects.get(id=id)
                PriceListdata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Price List Deleted Successfully', 'Data': []})
        except M_PriceList.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Price List Not available', 'Data': []})
        except IntegrityError:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Price List used in another table', 'Data': []})