from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, connection, transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_PartyItems import *
from ..models import *
from django.db.models import Count


class PartyItemsViewSecond(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def get(self, request,id=0):
            try:
                with transaction.atomic():
                    query = MC_PartyItems.objects.filter(Party_id = id)
                    # return JsonResponse({ 'query': str(query.query)})
                    if not query:
                        return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Items Not available', 'Data': []})
                    else:
                        Items_Serializer = MC_PartyItemSerializerThird(query, many=True).data
                        ItemList = list()
                        for a in Items_Serializer:
                            ItemList.append({
                                "id":a['id'],
                                "Item":a['Item']['id'],
                                "Name": a['Item']['Name'],
                                "Party":a['Party']['id']
                            })
                        return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data':ItemList })
            except Exception as e:
                return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
        
class PartyItemsView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication
    
    
    @transaction.atomic()
    def get(self, request,id=0):
            try:
                with transaction.atomic():
                  
                    # query=MC_PartyItems.objects.all().values('Party').annotate(total=Count('Item')).order_by('total')
                    query=MC_PartyItems.objects.raw('''select mc_partyitems.id,m_parties.Name, mc_partyitems.Party_id,count(mc_partyitems.Item_id)As Total From mc_partyitems join m_parties on m_parties.id=mc_partyitems.Party_id group by mc_partyitems.Party_id  ''')
                    # return JsonResponse({ 'query': str(query.query)})
                    if not query:
                        return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Items Not available', 'Data': []})
                    else:
                        Items_Serializer = MC_PartyItemSerializerFourth(query, many=True).data
                        # return JsonResponse({ 'query': Items_Serializer[0]})
                        ItemList = list()
                        for a in Items_Serializer:
                            ItemList.append({
                                "id":a['Party_id'],
                                "Name":a['Name'],
                                "Total": a['Total']
                            })
                        return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data':ItemList })
            except Exception as e:
                return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

    @transaction.atomic()
    def post(self, request,id=0):
        try:
            with transaction.atomic():
                PartyItems_data = JSONParser().parse(request)
                PartyItems_serializer = MC_PartyItemSerializer(data=PartyItems_data,many=True)
            if PartyItems_serializer.is_valid():
                id = PartyItems_serializer.data[0]['Party']
                MC_PartyItem_data = MC_PartyItems.objects.filter(Party=id)
                # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'PartyItems Save Successfully', 'Data' :str(MC_PartyItem_data.query)})
                MC_PartyItem_data.delete()
                # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'PartyItems Save Successfully', 'Data' :PartyItems_serializer.data[0]['Party']})
                PartyItems_serializer.save()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'PartyItems Save Successfully', 'Data' :[]})
            else:
                transaction.set_rollback(True)
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': PartyItems_serializer.errors, 'Data' : []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})