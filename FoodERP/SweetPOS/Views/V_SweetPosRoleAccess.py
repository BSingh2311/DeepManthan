import base64
from ..models import *
from ..Serializer.S_SweetPosRoleAccess import *
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from rest_framework.parsers import JSONParser

from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.authentication import BasicAuthentication
import pdb
from FoodERPApp.Views.V_CommFunction import create_transaction_logNew


def BasicAuthenticationfunction(request):
    auth_header = request.META.get('HTTP_AUTHORIZATION')
    if auth_header:
                    
        # Parsing the authorization header
        auth_type, auth_string = auth_header.split(' ', 1)
        if auth_type.lower() == 'basic':
            
            
            try:
                username, password = base64.b64decode(
                    auth_string).decode().split(':', 1)
            except (TypeError, ValueError, UnicodeDecodeError):
                return Response('Invalid authorization header', status=status.HTTP_401_UNAUTHORIZED)
                
        user = authenticate(request, username=username, password=password)
    return user



class SweetPosRoleAccessView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    
    @transaction.atomic()
    def post(self, request):
        try:  
            with transaction.atomic():
                SPOSRoleAccessdata = JSONParser().parse(request)
                response_data = []
                
                for data in SPOSRoleAccessdata:
                    
                    if 'Party' in data and M_SweetPOSRoleAccess.objects.using('sweetpos_db').filter(Party=data['Party']).exists():
                        obj = M_SweetPOSRoleAccess.objects.using('sweetpos_db').get(Party=data['Party'])
                        for key, value in data.items():
                           setattr(obj, key, value)
                        obj.save(using='sweetpos_db')
                        
                    else:
                       
                        obj = M_SweetPOSRoleAccess(**data)
                        obj.save(using='sweetpos_db')
                        

                log_entry = create_transaction_logNew(request, SPOSRoleAccessdata,SPOSRoleAccessdata['Party'],'',346,0)    

                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'SweetPosRoleAccess Save Successfully', 'Data':[]}) 
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0,0,'SweetPosRoleAccess Save:'+str(list(e)),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  list(e), 'Data':[]})
        
    @transaction.atomic()
    def get(self, request):
        try:
            with transaction.atomic():
                
                
                RoleAccessData = M_SweetPOSRoleAccess.objects.raw('''Select A.id, A.Name,A.id Party, B.*
                                        From FoodERP.M_Parties A
                                        Left Join SweetPOS.M_SweetPOSRoleAccess B on A.id = B.Party
                                        where A.PartyType_id = 19''')
                                        
                RoleAccess_serializer = SPOSRoleAccessSerializerSecond(RoleAccessData, many=True).data
                
                log_entry = create_transaction_logNew(request, RoleAccess_serializer,0,'',347,0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'','Data': RoleAccess_serializer})
        except  M_SweetPOSRoleAccess.DoesNotExist:
            log_entry = create_transaction_logNew(request, 0,0,'GETSweetPOSRoleAccessDetails'+'RoleAccess Not available',347,0)
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'RoleAccess Not available', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0,0,'GETSweetPOSRoleAccessDetails:'+str(Exception(e)),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})



class SPOSLog_inView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [BasicAuthentication]

    @transaction.atomic()
    def post(self, request ):
        SPOSLog_in_data = JSONParser().parse(request)
        try:
            
            with transaction.atomic():
               
                # pdb.set_trace()
                Division = SPOSLog_in_data['DivisionID']

                user=BasicAuthenticationfunction(request)
                    
                if user is not None:
                    obj = M_SweetPOSLogin(**SPOSLog_in_data)
                    obj.save(using='sweetpos_db')
                    
                    responce=M_SweetPOSRoleAccess.objects.using('sweetpos_db').get(Party=Division)
                    responce_serializer=SPOSRoleAccessSerializer(responce).data
                    
                    log_entry = create_transaction_logNew(request, SPOSLog_in_data,0,'',348,0)
                    return JsonResponse({"Success":True,"status_code":200,"msg":"Loged In Successfully..!","RoleAccess": responce_serializer})
                    

        except Exception as e:
            log_entry = create_transaction_logNew(request, SPOSLog_in_data,0,'SweetPOSLogin:'+str(Exception(e)),33,0)
            raise JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})