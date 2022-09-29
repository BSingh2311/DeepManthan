from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, connection, transaction
from rest_framework.parsers import JSONParser

from ..Serializer.S_Mrps import *

from ..Serializer.S_Items import *

from ..Serializer.S_Parties import *

from .V_CommFunction import *

from ..models import *


class M_MRPsView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def get(self, request):
        try:
            with transaction.atomic():
                MRPdata = M_MRPMaster.objects.raw('''SELECT m_mrpmaster.id,m_mrpmaster.EffectiveDate,m_mrpmaster.Company_id,m_mrpmaster.Division_id,m_mrpmaster.Party_id,c_companies.Name CompanyName,a.Name DivisionName,m_parties.Name PartyName  FROM m_mrpmaster left join c_companies on c_companies.id = m_mrpmaster.Company_id left join m_parties a on a.id = m_mrpmaster.Division_id left join m_parties on m_parties.id = m_mrpmaster.Party_id group by EffectiveDate,Party_id,Division_id Order BY EffectiveDate Desc''')
                # print(str(MRPdata.query))
                if not MRPdata:
                    return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Items Not available', 'Data': []})
                else:
                    MRPdata_Serializer = M_MRPsSerializerSecond(MRPdata, many=True).data
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': MRPdata_Serializer})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
    
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic(): 
                M_Mrpsdata = JSONParser().parse(request)
                M_Mrps_Serializer = M_MRPsSerializer(data=M_Mrpsdata,many=True)
            if M_Mrps_Serializer.is_valid():
                M_Mrps_Serializer.save()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'MRP Save Successfully','Data' :[]})
            else:
                transaction.set_rollback(True)
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': M_Mrps_Serializer.errors,'Data' :[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})


class GETMrpDetails(CreateAPIView): 
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                DivisionID = request.data['Division']
                PartyID = request.data['Party']
                EffectiveDate = request.data['EffectiveDate']
                query = M_Items.objects.all()
                if not query:
                    return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Items Not available', 'Data': []})
                else:
                    Items_Serializer = M_ItemsSerializer01(query, many=True).data
                    ItemList = list()
                    for a in Items_Serializer:
                        Item= a['id']
                        MRP = GetCurrentDateMRP(Item,DivisionID,PartyID,EffectiveDate)
                        ItemList.append({
                            "id": Item,
                            "Name": a['Name'],
                            "CurrentMRP": MRP,
                            "MRP":""
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data':ItemList })
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
    
    
    
    
           