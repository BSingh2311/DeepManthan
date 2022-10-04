from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, connection, transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_Group import *
from ..models import *


class GroupView(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                Groupquery = M_Group.objects.all()
                if Groupquery.exists():
                    # return JsonResponse({'query':  str(Itemsquery.query)})
                    Groupdata = GroupSerializerSecond(
                        Groupquery, many=True).data
                    GroupList = list()
                    for a in Groupdata:
                        GroupList.append({
                            "id": a['id'],
                            "Name": a['Name'],
                            "GroupType": a['GroupType']['id'],
                            "GroupTypeName": a['GroupType']['Name'],
                            "CreatedBy": a['CreatedBy'],
                            "CreatedOn": a['CreatedOn'],
                            "UpdatedBy": a['UpdatedBy'],
                            "UpdatedOn": a['UpdatedOn']
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': GroupList})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Group Not available ', 'Data': []})
        except M_Category.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':  'Group Not available', 'Data': []})

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                Group_data = JSONParser().parse(request)
                Group_Serializer = GroupSerializer(data=Group_data)
                if Group_Serializer.is_valid():
                    Group_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Group Save Successfully', 'Data': []})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  Group_Serializer.errors, 'Data': []})
        except Exception:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  'Exception', 'Data': []})

class GroupViewSecond(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def get(self, request,id=0):
        try:
            with transaction.atomic():
                Groupquery = M_Group.objects.filter(id=id)
                if Groupquery.exists():
                    # return JsonResponse({'query':  str(Itemsquery.query)})
                    Groupdata = GroupSerializerSecond(Groupquery, many=True).data
                    GroupList=list()
                    for a in Groupdata:
                        GroupList.append({
                            "id": a['id'],
                            "Name": a['Name'],
                            "GroupType": a['GroupType']['id'],
                            "GroupTypeName": a['GroupType']['Name'],
                            "CreatedBy": a['CreatedBy'],
                            "CreatedOn": a['CreatedOn'],
                            "UpdatedBy": a['UpdatedBy'],
                            "UpdatedOn": a['UpdatedOn']
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': GroupList[0]})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Group Not available ', 'Data': []})
        except M_Group.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Group Not available', 'Data': []})


    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                Group_data = JSONParser().parse(request)
                Group_dataByID = M_Group.objects.get(id=id)
                Group_Serializer = GroupSerializer(
                    Group_dataByID, data=Group_data)
                if Group_Serializer.is_valid():
                    Group_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Group Updated Successfully', 'Data':[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Group_Serializer.errors, 'Data':[]})
        except Exception  :
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  'Exception', 'Data':[]})
        

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                Group_data = M_Group.objects.get(id=id)
                Group_data.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Group Deleted Successfully', 'Data':[]})
        except M_Group.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Group Not available', 'Data': []})
        except IntegrityError:   
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Group used in another table', 'Data': []})   

class GetGroupByGroupTypeID(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request,id=0):
        try:
            with transaction.atomic():
                Groupquery = M_Group.objects.filter(GroupType_id=id)
                if Groupquery.exists():
                    # return JsonResponse({'query':  str(Itemsquery.query)})
                    Groupdata = GroupSerializerSecond(Groupquery, many=True).data
                    GroupList=list()
                    for a in Groupdata:
                        GroupList.append({
                            "id": a['id'],
                            "Name": a['Name'],
                            "GroupType": a['GroupType']['id'],
                            "GroupTypeName": a['GroupType']['Name'],
                            "CreatedBy": a['CreatedBy'],
                            "CreatedOn": a['CreatedOn'],
                            "UpdatedBy": a['UpdatedBy'],
                            "UpdatedOn": a['UpdatedOn']
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': GroupList})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Group Not available ', 'Data': []})
        except M_Group.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Group Not available', 'Data': []})
