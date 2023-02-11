from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, connection, transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_GRNs import *
from ..Serializer.S_VDCChallan import *
from ..Views.V_TransactionNumberfun import GetMaxNumber, GetPrifix
from ..models import  *

class VDCChallanViewSecond(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                GRNdata = T_GRNs.objects.get(id=id)
                GRN_serializer = T_GRNSerializerForGET(GRNdata).data
                # return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': GRN_serializer})
                GRNItemListData = list()
                for a in GRN_serializer['GRNItems']:
                    GRNItemListData.append({
                        "Item": a['Item']['id'],
                        "ItemName": a['Item']['Name'],
                        "Quantity": a['Quantity'],
                        "Unit": a['Unit']['id'],
                        "UnitName": a['Unit']['BaseUnitConversion'],
                        "BaseUnitQuantity": a['BaseUnitQuantity'],
                        "MRP": a['MRP'],
                        "ReferenceRate": a['ReferenceRate'],
                        "Rate": a['Rate'],
                        "BasicAmount": a['BasicAmount'],
                        "TaxType": a['TaxType'],
                        "GST": a['GST']['id'],
                        "GSTPercentage": a['GST']['GSTPercentage'],
                        "HSNCode": a['GST']['HSNCode'],
                        "GSTAmount": a['GSTAmount'],
                        "Amount": a['Amount'],
                        "DiscountType": a['DiscountType'],
                        "Discount": a['Discount'],
                        "DiscountAmount": a['DiscountAmount'],
                        "CGST": a['CGST'],
                        "SGST": a['SGST'],
                        "IGST": a['IGST'],
                        "CGSTPercentage": a['CGSTPercentage'],
                        "SGSTPercentage": a['SGSTPercentage'],
                        "IGSTPercentage": a['IGSTPercentage'],
                        "BatchDate": a['BatchDate'],
                        "BatchCode": a['BatchCode'],
                        "SystemBatchDate": a['SystemBatchDate'],
                        "SystemBatchCode": a['SystemBatchCode'],
                        
                    })

                GRNReferencesData = list()
                for r in GRN_serializer['GRNReferences']:
                    GRNReferencesData.append({
                        "GRN": r['GRN']
                    })
                GRNListData = list()
                a = GRN_serializer
                GRNListData.append({
                    "id": a['id'],
                    "InvoiceDate": a['GRNDate'],
                    "Customer": a['Customer']['id'],
                    "CustomerName": a['Customer']['Name'],
                    "GRNNumber": a['GRNNumber'],
                    "FullGRNNumber": a['FullGRNNumber'],
                    "InvoiceNumber": a['InvoiceNumber'],
                    "GrandTotal": a['GrandTotal'],
                    "Party": a['Party']['id'],
                    "PartyName": a['Party']['Name'],
                    "CreatedBy": a['CreatedBy'],
                    "UpdatedBy": a['UpdatedBy'],
                    "VDCChallanReferences": GRNReferencesData,
                    "VDCChallanItems": GRNItemListData
                })
                # return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': GRNListData[0]})
                Party = GRNListData[0]['Party']
                VDCChallanDate = GRNListData[0]['InvoiceDate']
                # ==========================Get Max Invoice Number=====================================================
                a = GetMaxNumber.GetVDCChallanNumber(Party,VDCChallanDate)
                GRNListData[0]['InvoiceNumber'] = a
                b = GetPrifix.GetVDCChallanprefix(Party)
                GRNListData[0]['FullInvoiceNumber'] = str(b)+""+str(a)
                #==================================================================================================
                # return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': GRNListData[0]}) 
                Invoice_serializer = VDCChallanSerializer(data=GRNListData[0])
                if Invoice_serializer.is_valid():
                    return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': Invoice_serializer, 'Data':[]})
                    
                    Invoice_serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'VDC Challan Save Successfully', 'Data':[]})
                return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': Invoice_serializer.errors, 'Data':[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
