from django.db.models import Q
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, connection, transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_PartySubParty import *
from ..Serializer.S_CompanyGroup import *
from ..models import *


class PartySubPartyView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request):
        try:
            with transaction.atomic():
                PartySubpartiesdata = MC_PartySubParty.objects.all()
                if PartySubpartiesdata.exists():
                    PartySubParty_Serializer = PartySubpartySerializerSecond(PartySubpartiesdata, many=True)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'', 'Data': PartySubParty_Serializer.data})
                return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Party SubParty Not available', 'Data': []})        
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
    
    
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                PartySubpartiesdata = JSONParser().parse(request)
                PartySubparties_Serializer = PartySubPartySerializer(data=PartySubpartiesdata, many=True)
                if PartySubparties_Serializer.is_valid():
                    PartySubparties_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Party Subparty Save Successfully', 'Data':[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': PartySubparties_Serializer.errors, 'Data':[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})

class PartySubPartyViewSecond(CreateAPIView): 
       
    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                query = MC_PartySubParty.objects.filter(Party_id=id)
                # return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '', 'Data': str(query.query)})
                PartySubparties_Serializer = PartySubpartySerializerSecond(query)
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '', 'Data': PartySubparties_Serializer.data})
        except  MC_PartySubParty.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Party SubParty Not available', 'Data': []})
        except Exception as e:
            raise JsonResponse({'StatusCode': 400, 'Status': True, 'Message':   'Execution Error', 'Data':[]})

class GetVendorSupplierCustomerListView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication 
            
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                Partydata = JSONParser().parse(request)
                Type=Partydata['Type']
                id=Partydata['PartyID']
                if(Type==1): #Vendor
                    aa=M_Parties.objects.filter(PartyType = 3).values('id') 
                    Query = MC_PartySubParty.objects.filter(Party=id,SubParty__in=aa)
                
                elif(Type==2): #Supplier
                    Query = MC_PartySubParty.objects.filter(SubParty=id)
                   
                else:  #Customer
                    aa=M_Parties.objects.exclude(PartyType = 3).values('id') 
                    Query = MC_PartySubParty.objects.filter(Party=id,SubParty__in=aa)
                
                if Query:
                    Supplier_serializer = PartySubpartySerializerSecond(Query, many=True).data
                    ListData = list()
                    for a in Supplier_serializer: 
                        if(Type==1): #Vendor
                            ListData.append({
                            "id": a['SubParty']['id'],
                            "Name": a['SubParty']['Name']
                            })   
                        elif(Type==2): #Supplier
                            ListData.append({
                            "id": a['Party']['id'],
                            "Name": a['Party']['Name']
                            }) 
                        else:  #Customer
                            ListData.append({
                            "id": a['SubParty']['id'],
                            "Name": a['SubParty']['Name']
                            })    
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'','Data': ListData})
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'Record Not Found','Data': []})
        except Exception as e:
                return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

