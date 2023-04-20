from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from ..Views.V_TransactionNumberfun import GetMaxNumber, GetPrifix
from ..Serializer.S_CreditDebit import *
from ..Serializer.S_Items import *
from django.db.models import Sum
from ..models import *


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
                a = GetMaxNumber.GetPurchaseReturnNumber(Party,Date)
                PurchaseReturndata['ReturnNo'] = str(a)
                b = GetPrifix.GetPurchaseReturnPrifix(Party)
                PurchaseReturndata['FullReturnNumber'] = b+""+str(a)
                PurchaseReturn_Serializer = PurchaseReturnSerializer(data=PurchaseReturndata)
                if PurchaseReturn_Serializer.is_valid():
                    PurchaseReturn_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Purchase Return Save Successfully', 'Data':[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  PurchaseReturn_Serializer.errors, 'Data':[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
    

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                PurchaseReturndata = T_PurchaseReturn.objects.get(id=id)
                PurchaseReturndata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Return Deleted Successfully', 'Data':[]})
        except IntegrityError:   
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Return used in another table', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
        
        
        
        
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
                    ItemData=list()
                    for a in Itemsdata:
                        UnitDetails=list()
                        for d in a['ItemUnitDetails']:
                            if d['IsDeleted']== 0 :
                                UnitDetails.append({
                                    "id": d['id'],
                                    "UnitID": d['UnitID']['id'],
                                    "UnitName": d['UnitID']['Name'],
                                    "BaseUnitQuantity": d['BaseUnitQuantity'],
                                    "IsBase": d['IsBase'],
                                    "PODefaultUnit": d['PODefaultUnit'],
                                    "SODefaultUnit": d['SODefaultUnit'],
                                
                                })
                        
                        MRPDetails=list()
                        for g in a['ItemMRPDetails']:
                            if g['IsDeleted']== 0 :
                                MRPDetails.append({
                                    "id": g['id'],
                                    "EffectiveDate": g['EffectiveDate'],
                                    "Company": g['Company']['id'],
                                    "CompanyName": g['Company']['Name'],
                                    "MRP": g['MRP'],
                                    "Party": g['Party']['id'],
                                    "PartyName": g['Party']['Name'],
                                    "Division":g['Division']['id'],
                                    "DivisionName":g['Division']['Name'],
                                    "CreatedBy":g['CreatedBy'],
                                    "UpdatedBy":g['UpdatedBy'],
                                    "IsAdd":False
                                })
                        
                        MarginDetails=list()
                        for h in a['ItemMarginDetails']:
                            if h['IsDeleted']== 0 :
                                MarginDetails.append({
                                    "id": h['id'],
                                    "EffectiveDate": h['EffectiveDate'],
                                    "Company": h['Company']['id'],
                                    "CompanyName": h['Company']['Name'],
                                    "Party": h['Party']['id'],
                                    "PartyName": h['Party']['Name'],
                                    "Margin": h['Margin'],
                                    "CreatedBy":h['CreatedBy'],
                                    "UpdatedBy":h['UpdatedBy'],
                                    "PriceList":h['PriceList']['id'],
                                    "PriceListName":h['PriceList']['Name'],
                                    "IsAdd":False   
                                })
                        
                        GSTHSNDetails=list()
                        for i in a['ItemGSTHSNDetails']:
                            if i['IsDeleted']== 0 :
                                GSTHSNDetails.append({
                                    "id": i['id'],
                                    "EffectiveDate": i['EffectiveDate'],
                                    "GSTPercentage": i['GSTPercentage'],
                                    "HSNCode": i['HSNCode'],
                                    "Company": i['Company']['id'],
                                    "CompanyName": i['Company']['Name'],
                                    "CreatedBy":i['CreatedBy'],
                                    "UpdatedBy":i['UpdatedBy'],
                                    "IsAdd":False
                                })
                        ItemData.append({
                            "id": a['id'],
                            "Name": a['Name'],
                            "ItemUnitDetails": UnitDetails, 
                            "ItemMRPDetails":MRPDetails,
                            "ItemMarginDetails":MarginDetails, 
                            "ItemGSTHSNDetails":GSTHSNDetails,
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': ItemData[0]})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Items Not available ', 'Data': []})
        except M_Items.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Items Not available', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})        
