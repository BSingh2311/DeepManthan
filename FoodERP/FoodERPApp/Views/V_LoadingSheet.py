from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, connection, transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_LoadingSheet import *
from ..Serializer.S_Invoices import *
from ..models import *
from ..Views.V_TransactionNumberfun import GetMaxNumber


class LoadingSheetListView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                Loadingsheetdata = JSONParser().parse(request)
                FromDate = Loadingsheetdata['FromDate']
                ToDate = Loadingsheetdata['ToDate']
                Party = Loadingsheetdata['PartyID']
                query = T_LoadingSheet.objects.filter(Date__range=[FromDate, ToDate], Party=Party)
                if query.exists():
                    LoadingSheet_Serializer = LoadingSheetListSerializer(query, many=True).data
                    LoadingSheetListData = list()
                    for a in LoadingSheet_Serializer:
                        LoadingSheetListData.append({
                            "id": a['id'],
                            "Date": a['Date'],
                            "LoadingSheetNo": a['No'],
                            "Route Name": a['Route']['Name'],
                            "TotalAmount": a['TotalAmount'],
                            "InvoiceCount": a['InvoiceCount'],
                            "VehicleNo": a['Vehicle']['VehicleNumber'],
                            "VehicleType": a['Vehicle']['VehicleType']['Name'],
                            "DriverName": a['Driver']['Name'],
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': LoadingSheetListData})
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Loading Sheet Not available', 'Data':[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})



class LoadingSheetView(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                Loadingsheetdata = JSONParser().parse(request)
                Party = Loadingsheetdata['Party']
                Date = Loadingsheetdata['Date']
                a = GetMaxNumber.GetLoadingSheetNumber(Party,Date)
                Loadingsheetdata['No'] = str(a)
                Loadingsheet_Serializer = LoadingSheetSerializer(data=Loadingsheetdata)
                if Loadingsheet_Serializer.is_valid():
                    Loadingsheet_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Loading Sheet Save Successfully', 'Data':[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  Loadingsheet_Serializer.errors, 'Data':[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
    
    @transaction.atomic()
    def get(self, request,id=0):
        try:
            with transaction.atomic():
                Loadingsheetquery = T_LoadingSheet.objects.filter(id=id)
                if Loadingsheetquery.exists():
                    LoadingSheetdata = LoadingSheetSerializer(Loadingsheetquery, many=True).data
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': LoadingSheetdata})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Loading Sheet Not available ', 'Data': []})
        except M_Routes.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Loading Sheet Not available', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})


    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                Loadingsheetdata = JSONParser().parse(request)
                LoadingsheetdataByID = T_LoadingSheet.objects.get(id=id)
                Loadingsheet_Serializer = LoadingSheetSerializer(LoadingsheetdataByID, data=Loadingsheetdata)
                if Loadingsheet_Serializer.is_valid():
                    Loadingsheet_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Loading Sheet Updated Successfully', 'Data':[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Loadingsheet_Serializer.errors, 'Data':[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
        

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                Loadingsheetdata = T_LoadingSheet.objects.get(id=id)
                Loadingsheetdata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Loading Sheet Deleted Successfully', 'Data':[]})
        except T_LoadingSheet.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Loading Sheet Not available', 'Data': []})
        except IntegrityError:   
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Loading Sheet used in another table', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
        
  
class LoadingSheetInvoicesView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request, id=0):
        try:
            with transaction.atomic():
                Invoicedata = JSONParser().parse(request)
                
                FromDate = Invoicedata['FromDate']
                ToDate = Invoicedata['ToDate']
                Party = Invoicedata['Party']
                Route = Invoicedata['Route']
                
                if(Route == ''):
                    query =  T_Invoices.objects.raw('''SELECT t_invoices.id as id, t_invoices.InvoiceDate, t_invoices.Customer_id, t_invoices.FullInvoiceNumber, t_invoices.GrandTotal, t_invoices.Party_id, t_invoices.CreatedOn,  t_invoices.UpdatedOn, m_parties.Name FROM t_invoices join m_parties on  m_parties.id=  t_invoices.Customer_id WHERE t_invoices.InvoiceDate BETWEEN %s AND %s AND t_invoices.Party_id = %s ''',[FromDate,ToDate,Party])
                else:
                    query =  T_Invoices.objects.raw('''SELECT t_invoices.id as id, t_invoices.InvoiceDate, t_invoices.Customer_id, t_invoices.FullInvoiceNumber, t_invoices.GrandTotal, t_invoices.Party_id, t_invoices.CreatedOn, t_invoices.UpdatedOn,m_parties.Name FROM t_invoices join m_parties on  m_parties.id=  t_invoices.Customer_id join mc_partysubparty on mc_partysubparty.SubParty_id = t_invoices.Customer_id and mc_partysubparty.Route_id =%s WHERE t_invoices.InvoiceDate BETWEEN %s AND %s AND t_invoices.Party_id=%s''', [Route,FromDate,ToDate,Party])
           
                if query:
                    Invoice_serializer = LoadingSheetInvoicesSerializer(query, many=True).data
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'','Data': Invoice_serializer})
                    InvoiceListData = list()
                    for a in Invoice_serializer:
                        InvoiceListData.append({
                            "id": a['id'],
                            "InvoiceDate": a['InvoiceDate'],
                            "FullInvoiceNumber": a['FullInvoiceNumber'],
                            "Customer": a['Name'],
                            "CustomerID": a['Customer_id'],
                            "PartyID": a['Party_id'],
                            "GrandTotal": a['GrandTotal'],
                            "CreatedOn": a['CreatedOn'] 
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': InvoiceListData})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Record Not Found', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})


class LoadingSheetPrintView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication
    
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                query = T_LoadingSheet.objects.filter(id=id)
                LoadingSheet_Serializer = LoadingSheetListSerializer(query, many=True).data
                InvoiceData = list()
                LoadingSheetListData = list()
                for a in LoadingSheet_Serializer:
                    query = MC_PartyAddress.objects.filter(Party=a['Party'])
                    LoadingSheetListData.append({
                        "id": a['id'],
                        "Date": a['Date'],
                        "Party":a['Party']['Name'],
                        "PartyAddress":a['Party']['PartyAddress'][0],
                        "LoadingSheetNo": a['No'],
                        "Route Name": a['Route']['Name'],
                        "TotalAmount": a['TotalAmount'],
                        "InvoiceCount": a['InvoiceCount'],
                        "VehicleNo": a['Vehicle']['VehicleNumber'],
                        "VehicleType": a['Vehicle']['VehicleType']['Name'],
                        "DriverName": a['Driver']['Name'],
                    })
                 
                q1 = TC_LoadingSheetDetails.objects.filter(LoadingSheet=id).values('Invoice') 
                InvoiceQuery = T_Invoices.objects.filter(id__in=q1)
                if InvoiceQuery.exists():
                    InvoiceSerializedata = InvoiceSerializerSecond(InvoiceQuery, many=True).data
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': InvoiceSerializedata})
                    InvoiceParent = list()
                    InvoiceItemDetails = list()
                    for a in InvoiceSerializedata:
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
                        InvoiceParent.append({
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
                        })
                    InvoiceData.append({
                        "PartyDetails":LoadingSheetListData[0],
                        "InvoiceItems":InvoiceItemDetails,
                        "InvoiceParent":InvoiceParent,
                    })    
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': InvoiceData[0] })
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Order Data Not available ', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
