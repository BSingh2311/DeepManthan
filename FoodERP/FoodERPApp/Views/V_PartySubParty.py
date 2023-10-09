from django.db.models import Q
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_Parties import DivisionsSerializer
from ..Serializer.S_PartySubParty import *
from ..Serializer.S_CompanyGroup import *
from ..models import *
from .V_CommFunction import *

class PartySubPartyListFilterView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def get(self, request):
        try:
            with transaction.atomic():
                query = MC_PartySubParty.objects.raw('''SELECT MC_PartySubParty.id,MC_PartySubParty.Party_id,M_Parties.Name PartyName,count(MC_PartySubParty.SubParty_id)Subparty FROM MC_PartySubParty join M_Parties ON M_Parties.id=MC_PartySubParty.Party_id group by Party_id''')
                if not query:
                    log_entry = create_transaction_logNew(request, 0,0,'Party SubParty List Not Found',175,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Records Not Found', 'Data': []})
                else:
                    M_Items_Serializer = PartySubPartySerializerGETList(query, many=True).data
                    log_entry = create_transaction_logNew(request, M_Items_Serializer,0,'',175,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': M_Items_Serializer})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0,0,Exception(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
    
class PartySubPartyView(CreateAPIView):     # PartySubParty Save
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                PartySubpartiesdata = JSONParser().parse(request)
         
                PartySubparties_Serializer = PartySubPartySerializer(data=PartySubpartiesdata, many=True)
               
                if PartySubparties_Serializer.is_valid():
                    PartySubpartiesdata1 = MC_PartySubParty.objects.filter(Party=PartySubpartiesdata[0]['PartyID'])
                 
                    PartySubpartiesdata1.delete()
                    PartySubpartiesdata2 = MC_PartySubParty.objects.filter(SubParty=PartySubpartiesdata[0]['PartyID'],Party__PartyType=3).select_related('Party')
                  
                    PartySubpartiesdata2.delete()
                    
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Party SubParty Save Successfully', 'Data':str(PartySubpartiesdata.query)})
                   
                    SubParty = PartySubparties_Serializer.save()
                    LastInsertID = SubParty[0].id
                    log_entry = create_transaction_logNew(request, PartySubpartiesdata,PartySubpartiesdata[0]['Party'],'TransactionID:'+str(LastInsertID),176,LastInsertID)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Party SubParty Save Successfully', 'TransactionID':LastInsertID, 'Data':[]})
                else:
                    log_entry = create_transaction_logNew(request, PartySubpartiesdata,0,PartySubparties_Serializer.errors,34,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': PartySubparties_Serializer.errors, 'Data':[]})
        except Exception as e:
            log_entry = create_transaction_logNew(request, PartySubpartiesdata,0,Exception(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})

class PartySubPartyViewSecond(CreateAPIView): 
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication
       
    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                query= MC_PartySubParty.objects.filter(Party=id)
                
                SubPartySerializer = PartySubpartySerializerSecond(query, many=True).data
                
                query1= MC_PartySubParty.objects.filter(SubParty=id).values('Party_id')
                query2 = M_Parties.objects.filter(id__in=query1,PartyType__IsVendor=1).select_related('PartyType')
                query3 =  MC_PartySubParty.objects.filter(Party__in=query2)
                PartySerializer = PartySubpartySerializerSecond(query3, many=True).data
               
                
                SubPartyList = list()
                for a in PartySerializer:
                    SubPartyList.append({
                        "Party": a['SubParty']['id'],
                        "PartyName": a['SubParty']['Name'],
                        "SubParty": a['Party']['id'],
                        "SubPartyName": a['Party']['Name'],
                        "PartyType": a['Party']['PartyType']['id'],
                        "IsVendor": a['Party']['PartyType']['IsVendor'],
                        "Route": a['Route']['id'],
                        "Creditlimit": a['Creditlimit']
                    }) 
                for a in SubPartySerializer:
                    SubPartyList.append({
                        "Party": a['Party']['id'],
                        "PartyName": a['Party']['Name'],
                        "SubParty": a['SubParty']['id'],
                        "SubPartyName": a['SubParty']['Name'],
                        "PartyType": a['SubParty']['PartyType']['id'],
                        "IsVendor": a['SubParty']['PartyType']['IsVendor'],
                        "Route": a['Route']['id'],
                        "Creditlimit": a['Creditlimit']
                    })
                   
                
                log_entry = create_transaction_logNew(request, PartySerializer,a['Party']['id'],'',175,0)               
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': SubPartyList})
        except  MC_PartySubParty.DoesNotExist:
            log_entry = create_transaction_logNew(request, PartySerializer,PartySerializer[0]['Party'],'PartySubPartyList Not Available',175,0)
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Party SubParty Not available', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, PartySerializer,0,Exception(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})

class GetVendorSupplierCustomerListView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication 
            
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                Partydata = JSONParser().parse(request)
                Type=Partydata['Type']
                id=Partydata['PartyID']
                Company=Partydata['Company']
                Route = Partydata['Route']
                
                if(Type==1): #Vendor
                    q0=M_PartyType.objects.filter(Company=Company,IsVendor=1)
                    Query = MC_PartySubParty.objects.filter(SubParty=id,Party__PartyType__in=q0).select_related('Party')
                    
                elif(Type==2): #Supplier
                    q=C_Companies.objects.filter(id=Company).values("CompanyGroup")
                    q00=C_Companies.objects.filter(CompanyGroup=q[0]["CompanyGroup"])
                    q0=M_PartyType.objects.filter(Company__in=q00,IsVendor=0)
                    Query = MC_PartySubParty.objects.filter(SubParty=id,Party__PartyType__in=q0).select_related('Party')
                    
                elif(Type==3):  #Customer
                    q0=M_PartyType.objects.filter(Company=Company,IsVendor=0)
                    if (Route==""):
                        Query = MC_PartySubParty.objects.filter(Party=id,SubParty__PartyType__in=q0).select_related('Party')
                    else:
                        Query = MC_PartySubParty.objects.filter(Party=id,SubParty__PartyType__in=q0,Route=Route).select_related('Party')
                
                elif(Type==5):  #Customer without retailer
                    q0=M_PartyType.objects.filter(IsVendor=0,IsRetailer=0)
                    if (Route==""):
                        Query = MC_PartySubParty.objects.filter(Party=id,SubParty__PartyType__in=q0).select_related('Party')
                    else:
                        Query = MC_PartySubParty.objects.filter(Party=id,SubParty__PartyType__in=q0,Route=Route).select_related('Party')
                        
                    

                elif (Type==4):
                    Query = M_Parties.objects.filter(Company=Company,IsDivision=1).filter(~Q(id=id))
                
                if Query:
                    
                    if(Type==4):
                        Supplier_serializer = PartySerializer(Query, many=True).data
                    else:    
                        Supplier_serializer = PartySubpartySerializerSecond(Query, many=True).data
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'','Data': Supplier_serializer})
                    ListData = list()
                    FSSAINo= " "
                    FSSAIExipry = ""
                    for a in Supplier_serializer: 
                        if(Type==1): #Vendor
                            
                            if(a['Party']['PartyAddress'][0]['IsDefault'] == 1):
                                FSSAINo=a['Party']['PartyAddress'][0]['FSSAINo']
                                FSSAIExipry=a['Party']['PartyAddress'][0]['FSSAIExipry']
                              
                            ListData.append({
                            "id": a['Party']['id'],
                            "Name": a['Party']['Name'],
                            "GSTIN": a['Party']['GSTIN'],
                            "PAN":a['SubParty']['PAN'],
                            "FSSAINo" : FSSAINo,
                            "FSSAIExipry" : FSSAIExipry,
                            "IsTCSParty":a['IsTCSParty']
                            })   
                        elif(Type==2): #Supplier
                            if(a['Party']['PartyAddress'][0]['IsDefault'] == 1):
                                FSSAINo=a['Party']['PartyAddress'][0]['FSSAINo']
                                FSSAIExipry=a['Party']['PartyAddress'][0]['FSSAIExipry']
                                 
                            ListData.append({
                            "id": a['Party']['id'],
                            "Name": a['Party']['Name'],
                            "GSTIN": a['Party']['GSTIN'],
                            "PAN":a['SubParty']['PAN'],
                            "FSSAINo" : FSSAINo,
                            "FSSAIExipry" : FSSAIExipry,
                            "IsTCSParty":a['IsTCSParty']

                            }) 
                        elif(Type==3 or Type == 5 ):  #Customer
                            if(a['SubParty']['PartyAddress'][0]['IsDefault'] == 1):
                                FSSAINo=a['SubParty']['PartyAddress'][0]['FSSAINo']
                                FSSAIExipry=a['SubParty']['PartyAddress'][0]['FSSAIExipry']
                            
                            ListData.append({
                            "id": a['SubParty']['id'],
                            "Name": a['SubParty']['Name'],
                            "GSTIN": a['SubParty']['GSTIN'],
                            "PAN":a['SubParty']['PAN'],
                            "FSSAINo" : FSSAINo,
                            "FSSAIExipry" : FSSAIExipry,
                            "IsTCSParty":a['IsTCSParty'],
                          
                            })
                        else:
                            if(a['Party']['PartyAddress'][0]['IsDefault'] == 1):
                                FSSAINo=a['Party']['PartyAddress'][0]['FSSAINo']
                                FSSAIExipry=a['Party']['PartyAddress'][0]['FSSAIExipry']
                                

                            ListData.append({
                            "id": a['id'],
                            "Name": a['Name'],
                            "GSTIN": a['Party']['GSTIN'],
                            "PAN":a['SubParty']['PAN'],
                            "FSSAINo" : FSSAINo,
                            "FSSAIExipry" : FSSAIExipry,
                            "IsTCSParty":a['IsTCSParty']
                            })
                    log_entry = create_transaction_logNew(request, Partydata,id,'',177,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'','Data': ListData})
                log_entry = create_transaction_logNew(request, Partydata,id,'GetVendorSupplierCustomer Not Available',177,0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'Record Not Found','Data': []})
        except Exception as e:
                log_entry = create_transaction_logNew(request, Partydata,0,Exception(e),33,0)
                return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
                
        
class RetailerandSSDDView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication 
    
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                PartySubPartydata = JSONParser().parse(request)
                CompanyID=PartySubPartydata['CompanyID']
                PartyID=PartySubPartydata['PartyID']
                Type=PartySubPartydata['Type']   
                
                if Type==1: ##All Retailer under given Party and Company
                    q0=M_PartyType.objects.filter(Company=CompanyID,IsRetailer=1,IsSCM=1)
                    q1=MC_PartySubParty.objects.filter(Party=PartyID).values('SubParty')
                    q2=M_Parties.objects.filter(PartyType__in=q0,id__in=q1)
                  
                elif Type==2:  ##All SS/DD under given Party and Company
                    
                    q0=M_PartyType.objects.filter(Company=CompanyID,IsRetailer=0,IsSCM=1)
                    q1=MC_PartySubParty.objects.filter(Party=PartyID).values('SubParty')
                    q2=M_Parties.objects.filter(PartyType__in=q0,id__in=q1)
                
                elif Type==3:  #All SS/DD under given Company
                   
                    q=C_Companies.objects.filter(id=CompanyID).values('IsSCM')
                 
                    if q[0]['IsSCM'] == 0:
                       
                        
                        q2=M_Parties.objects.filter(Company=CompanyID )
                        
                    else:
                        a=C_Companies.objects.filter(id=CompanyID).values('CompanyGroup')
                     
                        a1=C_Companies.objects.filter(CompanyGroup=a[0]['CompanyGroup'])
                       
                        q0=M_PartyType.objects.filter(Company__in=a1,IsRetailer=0,IsSCM=1,IsDivision=0)
                       
                        q2=M_Parties.objects.filter(PartyType__in=q0)
                       
                
                elif Type==4:  #All Subparties under given Party and Company
                    q1=MC_PartySubParty.objects.filter(Party=PartyID).values('SubParty')
                    q2=M_Parties.objects.filter(id__in=q1)    
                
                PartySerializer_data=PartySerializer(q2,many=True).data
            log_entry = create_transaction_logNew(request, PartySubPartydata,PartyID,'',178,0)
            return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': PartySerializer_data})  
        except Exception as e:
            log_entry = create_transaction_logNew(request, PartySubPartydata,0,Exception(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})        
        
