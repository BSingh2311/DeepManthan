from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser

from ..Serializer.S_Drivers import *

from ..models import *


class DriverViewList(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                Driverdata = JSONParser().parse(request)
                Company = Driverdata['CompanyID']
                Party = Driverdata['PartyID']
                DriverNamedata = M_Drivers.objects.filter(Party=Party,Company=Company)
                if DriverNamedata.exists():
                    Drivers_Serializer = M_DriverSerializer(
                        DriverNamedata, many=True)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': Drivers_Serializer.data})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':  'Drivers Not Available', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

    
    
class DriverView(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def post(self, request, id=0):
        try:
            with transaction.atomic():
                Driverdata = JSONParser().parse(request)
                Driver_Serializer = M_DriverSerializer(data=Driverdata)
            if Driver_Serializer.is_valid():
                Driver_Serializer.save()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Driver Save Successfully', 'Data': []})
            else:
                transaction.set_rollback(True)
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Driver_Serializer.errors, 'Data': []})
        except Exception as e:
            raise JsonResponse(
                {'StatusCode': 400, 'Status': True, 'Message': str(e), 'Data': []})

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                Driverdata = M_Drivers.objects.get(id=id)
                Driver_Serializer = M_DriverSerializer(Driverdata)
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '', 'Data': Driver_Serializer.data})
        except  M_Drivers.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Driver Not available', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})   

    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                Driverdata = JSONParser().parse(request)
                DriverdataByID = M_Drivers.objects.get(id=id)
                Driver_Serializer = M_DriverSerializer(
                    DriverdataByID, data=Driverdata)
                if Driver_Serializer.is_valid():
                    Driver_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Driver Updated Successfully','Data' :[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Driver_Serializer.errors, 'Data' :[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})   

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                Driverdata = M_Drivers.objects.get(id=id)
                Driverdata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Driver Deleted Successfully','Data':[]})
        except M_Drivers.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Driver Not available', 'Data': []})
        except IntegrityError:   
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Driver used in another table', 'Data': []})