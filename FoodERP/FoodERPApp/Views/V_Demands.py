from typing import Concatenate
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, connection, transaction
from rest_framework.parsers import JSONParser
from ..Views.V_TransactionNumberfun import GetMaxNumber, GetPrifix
from ..Serializer.S_Demands import *
from ..Serializer.S_Items import *
from ..Serializer.S_PartyItems import *
from ..Serializer.S_Bom import *
from django.db.models import Sum
from ..models import *

class InterBranchDivisionView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request, id=0):
        try:
            with transaction.atomic():
                Divisiondata = JSONParser().parse(request)
                Company = Divisiondata['Company']
                Party = Divisiondata['Party']
                query = M_Parties.objects.filter(Company=Company,IsDivision=1).filter(~Q(id=Party))
                if query:
                    party_serializer = DivisionsSerializer(query, many=True).data
                    DivisionListData = list()
                    for a in party_serializer:
                        DivisionListData.append({
                            "id": a['id'],
                            "Name": a['Name']
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': DivisionListData})
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Record Not Found', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
    
class InterBranchItemsView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    def post(self, request):

        try:
            with transaction.atomic():
                # DivisionID = request.data['Division']
                Party = request.data['Supplier']  # Demand Page Supplier DropDown
               
                Customer = request.data['Customer']
                EffectiveDate = request.data['EffectiveDate']
                DemandID = request.data['DemandID']

                Itemquery = TC_DemandItems.objects.raw('''select a.id, a.Item_id,M_Items.Name ItemName,a.Quantity,a.MRP_id,m_mrpmaster.MRP MRPValue,a.Rate,a.Unit_id,m_units.Name UnitName,a.BaseUnitQuantity,a.GST_id,m_gsthsncode.GSTPercentage,
m_gsthsncode.HSNCode,a.Margin_id,m_marginmaster.Margin MarginValue,a.BasicAmount,a.GSTAmount,a.CGST,a.SGST,a.IGST,a.CGSTPercentage,a.SGSTPercentage,a.IGSTPercentage,a.Amount,a.Comment,M_Items.Sequence 
                from
((SELECT 0 id,`Item_id`,`Quantity`, `MRP_id`, `Rate`, `Unit_id`, `BaseUnitQuantity`, `GST_id`, `Margin_id`, `BasicAmount`, `GSTAmount`, `CGST`, `SGST`, `IGST`, `CGSTPercentage`, `SGSTPercentage`, `IGSTPercentage`, `Amount`,`Comment`
FROM `tc_demanditems` WHERE (`tc_demanditems`.`IsDeleted` = False AND `tc_demanditems`.`Demand_id` = %s)) 
UNION 
(SELECT 1 id,m_items.id `Item_id`, NULL AS `Quantity`, NULL AS `MRP`, NULL AS `Rate`, NULL AS `Unit`, NULL AS `BaseUnitQuantity`, NULL AS `GST`, NULL AS `Margin`, NULL AS `BasicAmount`, NULL AS `GSTAmount`, NULL AS `CGST`, NULL AS `SGST`, NULL AS `IGST`, NULL AS `CGSTPercentage`, NULL AS `SGSTPercentage`, NULL AS `IGSTPercentage`, NULL AS `Amount`,NULL AS `Comment` 
FROM `m_items` Join mc_partyitems a On m_items.id = a.Item_id
join mc_partyitems b On m_items.id = b.Item_id  WHERE M_Items.IsActive=1 and  a.Party_id =%s AND b.Party_id =%s))a

join m_items on m_items.id=a.Item_id 
left join m_mrpmaster on m_mrpmaster.id =a.MRP_id
left join mc_itemunits on mc_itemunits.id=a.Unit_id
left join m_units on m_units.id=mc_itemunits.UnitID_id
left join m_gsthsncode on m_gsthsncode.id=a.GST_id
left join m_marginmaster on m_marginmaster.id=a.Margin_id group by Item_id Order By m_items.Sequence''', ([DemandID], [Party], [Customer]))
               
                DemandItemSerializer = DemandEditserializer(
                    Itemquery, many=True).data
                # return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  '', 'Data': OrderItemSerializer})

                for b in DemandItemSerializer:
                    ItemID = b['Item_id']
                    GSTID = b['GST_id']
            # =====================GST================================================
                    if GSTID is None:
                        Gst = GSTHsnCodeMaster(
                            ItemID, EffectiveDate).GetTodaysGstHsnCode()
                        b['GST_id'] = Gst[0]['Gstid']
                        b['GSTPercentage'] = Gst[0]['GST']
            # =====================Stock================================================

                    stockquery = O_BatchWiseLiveStock.objects.filter(
                        Item=ItemID, Party=Customer).aggregate(Qty=Sum('BaseUnitQuantity'))
                    if stockquery['Qty'] is None:
                        Stock = 0.0
                    else:
                        Stock = stockquery['Qty']
            # =====================Rate================================================

                    ratequery = TC_DemandItems.objects.filter(
                        Item_id=ItemID).values('Rate').order_by('-id')[:1]
                    if not ratequery:
                        r = 0.00
                    else:
                        r = ratequery[0]['Rate']

                    if b['Rate'] is None:
                        b['Rate'] = r
            # =====================Rate================================================
                    UnitDetails = list()
                    ItemUnitquery = MC_ItemUnits.objects.filter(
                        Item=ItemID, IsDeleted=0)
                    ItemUnitqueryserialize = Mc_ItemUnitSerializerThird(
                        ItemUnitquery, many=True).data

                    for d in ItemUnitqueryserialize:
                        baseunitconcat = ShowBaseUnitQtyOnUnitDropDown(
                            ItemID, d['id'], d['BaseUnitQuantity']).ShowDetails()
                        UnitDetails.append({
                            "UnitID": d['id'],
                            "UnitName": d['UnitID']['Name'] + str(baseunitconcat),
                            "BaseUnitQuantity": d['BaseUnitQuantity'],
                            "PODefaultUnit": d['PODefaultUnit'],
                            "SODefaultUnit": d['SODefaultUnit'],


                        })
            # =====================IsDefaultTermsAndConditions================================================

                    b.update({"StockQuantity": Stock,
                              "UnitDetails": UnitDetails
                              })

                if DemandID != 0:
                    DemandQuery = T_Demands.objects.get(id=DemandID)
                    a = TC_DemandSerializerThird(DemandQuery).data

                    DemandData = list()
                    DemandData.append({
                        "id": a['id'],
                        "DemandDate": a['DemandDate'],
                        "DemandNo": a['DemandNo'],
                        "FullDemandNumber": a['FullDemandNumber'],
                        "DemandAmount": a['DemandAmount'],
                        "Description": a['Description'],
                        "Customer": a['Customer']['id'],
                        "CustomerName": a['Customer']['Name'],
                        "Supplier": a['Supplier']['id'],
                        "SupplierName": a['Supplier']['Name'],
                        "BillingAddressID": a['BillingAddress']['id'],
                        "BillingAddress": a['BillingAddress']['Address'],
                        "ShippingAddressID": a['ShippingAddress']['id'],
                        "ShippingAddress": a['ShippingAddress']['Address'],
                        "MaterialIssue":a['MaterialIssue'],
                        "DemandItems": DemandItemSerializer,
                        
                    })
                    FinalResult = DemandData[0]
                else:

                    NewDemand = list()
                    NewDemand.append({
                        "id": "",
                        "DemandDate": "",
                        "DemandNo":"",
                        "FullDemandNumber":"",
                        "DemandAmount": "",
                        "Description": "",
                        "Customer": "",
                        "CustomerName": "",
                        "Supplier": "",
                        "SupplierName": "",
                        "BillingAddressID": "",
                        "BillingAddress": "",
                        "ShippingAddressID": "",
                        "ShippingAddress": "",
                        "MaterialIssue":"",
                        "DemandItems": DemandItemSerializer,
                    })

                    FinalResult = NewDemand[0]

                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':  '', 'Data': FinalResult})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  e, 'Data': []})    
    
    

class DemandListFilterView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request, id=0):
        try:
            with transaction.atomic():
                Demanddata = JSONParser().parse(request)
                FromDate = Demanddata['FromDate']
                ToDate = Demanddata['ToDate']
                Customer = Demanddata['Customer'] # Customer Compansary
                Supplier = Demanddata['Supplier']
                
                if(Supplier == ''):
                    query = T_Demands.objects.filter(DemandDate__range=[FromDate, ToDate],Customer_id=Customer)
                else:
                    query = T_Demands.objects.filter(DemandDate__range=[FromDate, ToDate], Customer_id=Customer, Supplier_id=Supplier)
                # return JsonResponse({'query': str(Orderdata.query)})
                if query:
                    Demand_serializer = T_DemandSerializerSecond(query, many=True).data
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'','Data': Demand_serializer})
                    DemandListData = list()
                    for a in Demand_serializer:
                       
                        DemandListData.append({
                            "id": a['id'],
                            "DemandDate": a['DemandDate'],
                            "FullDemandNumber": a['FullDemandNumber'],
                            "CustomerID": a['Customer']['id'],
                            "Customer": a['Customer']['Name'],
                            "SupplierID": a['Supplier']['id'],
                            "Supplier": a['Supplier']['Name'],
                            "DemandAmount": a['DemandAmount'],
                            # "BillingAddress": a['BillingAddress']['Address'],
                            # "ShippingAddress": a['ShippingAddress']['Address'],
                            "CreatedBy": a['CreatedBy'],
                            "CreatedOn": a['CreatedOn'],
                         
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': DemandListData})
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Record Not Found', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})


class DemandView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                Demanddata = JSONParser().parse(request)
                Division = Demanddata['Division']
                Customer = Demanddata['Customer']
                DemandDate = Demanddata['DemandDate']

                '''Get Max Demand Number'''
                a = GetMaxNumber.GetDemandNumber(Division, Customer, DemandDate)
                # return JsonResponse({'StatusCode': 200, 'Status': True,   'Data':[] })
                for aa in Demanddata['DemandItem']:
                    BaseUnitQuantity=UnitwiseQuantityConversion(aa['Item'],aa['Quantity'],aa['Unit'],0,0,0).GetBaseUnitQuantity()
                    aa['BaseUnitQuantity'] =  BaseUnitQuantity 
                
                Demanddata['DemandNo'] = a
                '''Get Demand Prifix '''
                b = GetPrifix.GetDemandPrifix(Division)
                Demanddata['FullDemandNumber'] = b+""+str(a)
               
                Demand_serializer = T_DemandSerializer(data=Demanddata)
                if Demand_serializer.is_valid():
                    Demand_serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'Demand Save Successfully', 'Data': []})
                return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': Demand_serializer.errors, 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})


class DemandViewSecond(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication  
    
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                Demandupdatedata = JSONParser().parse(request)
                DemandupdateByID = T_Demands.objects.get(id=id)
                Demandupdate_Serializer = T_DemandSerializer(
                    DemandupdateByID, data=Demandupdatedata)
                if Demandupdate_Serializer.is_valid():
                    Demandupdate_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Demand Updated Successfully', 'Data': []})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': Demandupdate_Serializer.errors, 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})    
        
        
    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                Demand_Data = T_Demands.objects.get(id=id)
                Demand_Data.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Demand Deleted Successfully', 'Data': []})
        except T_Demands.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Record Not available', 'Data': []})
        except IntegrityError:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'This Transaction used in another table', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
