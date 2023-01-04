from sys import modules
from urllib import response
from django.http import JsonResponse
from rest_framework.response import Response

from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import connection, transaction
from rest_framework.parsers import JSONParser

from ..Serializer.S_RoleAccess import *
from ..models import *


def GetRelatedPageID(id):
    a=M_Pages.objects.filter(id=id).values('RelatedPageID','ActualPagePath') 
   
    if(a[0]['RelatedPageID']  == 0):
        b=M_Pages.objects.filter(RelatedPageID=id).values('id','ActualPagePath')
        return str(b[0]['id']) +','+ b[0]['ActualPagePath']
    else:
        return str(a[0]['RelatedPageID']) +','+ a[0]['ActualPagePath']


class RoleAccessView(RetrieveAPIView):

    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    def get(self, request, PartyID=0, EmployeeID=0):    
        
        Company="M_RoleAccess.Company_id is null"
        Division=PartyID
        # print(request.session.get('UserName'))
      
        if (int(PartyID) > 0)  : 
            Division="M_RoleAccess.Division_id = "+PartyID
            Role=MC_UserRoles.objects.raw('''SELECT Role_id id FROM mc_userroles join m_users on m_users.id=mc_userroles.User_id where Party_id= %s and m_users.Employee_id=%s''',[PartyID,EmployeeID])
        else:
            Division="M_RoleAccess.Division_id is null "
            Role=MC_UserRoles.objects.raw('''SELECT Role_id id FROM mc_userroles join m_users on m_users.id=mc_userroles.User_id where Party_id IS NULL and m_users.Employee_id=%s ''',[EmployeeID])
           
        # return Response(str(Role.query))
        qq = M_RoleAccessSerializerforRole(Role, many=True).data
        
       
        if(len(qq) == 1):
            roles=list()
            roles.append(qq[0]['id'])
            roles.append(0)
            y=tuple(roles)
            
        else:     
            roles=list()
            for a in qq:
                roles.append(a['id'])
            y=tuple(roles)

            
        

        if (int(PartyID) > 0)  :
       
            modules= M_RoleAccess.objects.filter(Division=PartyID ,Company_id__isnull=True, Role_id__in=y).values('Modules_id').distinct()   
        else:
            modules= M_RoleAccess.objects.filter(Division__isnull=True ,Company_id__isnull=True, Role_id__in=y).values('Modules_id').distinct()   

        queryset=H_Modules.objects.filter(id__in=modules).order_by("DisplayIndex")
        serializerdata = H_ModulesSerializer(queryset, many=True).data

        
        Moduledata = list()
               
        for a in serializerdata:
            id = a['id']
            Modulesdata = H_Modules.objects.get(id=id)
            Modules_Serializer = H_ModulesSerializer(Modulesdata).data
             

    
            if (int(PartyID) > 0)  :

                query=M_RoleAccess.objects.all().filter(Role_id__in=y,Modules_id=id,Division_id=PartyID,Company_id__isnull=True,)
            else :
                query=M_RoleAccess.objects.all().filter(Role_id__in=y,Modules_id=id,Division_id__isnull=True,Company_id__isnull=True)

            # print(str(query.query) )  
          
            PageSerializer = RoleAccessserializerforsidemenu(query,  many=True).data
            # return Response(PageSerializer ) 
            Pagesdata = list()
            for a1 in PageSerializer:
                id = a1['id']
               
                RolePageAccess = MC_RolePageAccess.objects.raw(''' SELECT mc_rolepageaccess.PageAccess_id id,Name  FROM mc_rolepageaccess 
                JOIN h_pageaccess ON h_pageaccess.id=mc_rolepageaccess.PageAccess_id  WHERE mc_rolepageaccess.RoleAccess_id=%s ''', [id])
                RolePageAccessSerializer = MC_RolePageAccessSerializer(
                    RolePageAccess,  many=True).data
                # print(str(RolePageAccess.query))
                GetRelatedPageIDData=GetRelatedPageID(a1['Pages']['id'])
                vvv=GetRelatedPageIDData.split(',')
                print(vvv)
                Pagesdata.append({
                    "id": a1['Pages']['id'], 
                    "RelatedPageID": vvv[0],
                    "RelatedPageIDPath": vvv[1],
                    "Name": a1['Pages']['PageType'],
                    "PageType" : a1['Pages']['PageType'],
                    "PageHeading": a1['Pages']['PageHeading'],
                    "PageDescription": a1['Pages']['PageDescription'],
                    "PageDescriptionDetails": a1['Pages']['PageDescriptionDetails'],
                    "DisplayIndex": a1['Pages']['DisplayIndex'],
                    "Icon": a1['Pages']['Icon'],
                    "ActualPagePath": a1['Pages']['ActualPagePath'],
                    "RolePageAccess": RolePageAccessSerializer
                })

            response1 = {
                "ModuleID": a['id'],
                "ModuleName":a["Name"],
                "ModuleData": Pagesdata,

            }
            Moduledata.append(response1)

        response = {
            "StatusCode": 200,
            "Status": True,
            "Message": " ",
            "Data": Moduledata,
        }
        return Response(response)

    # Role Access POST Method first delete record on role,company,division and then Insert data

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                RoleAccessdata = JSONParser().parse(request)
                RoleAccessSerialize_data = M_RoleAccessSerializer(
                    data=RoleAccessdata, many=True)
                if RoleAccessSerialize_data.is_valid():
                    # return JsonResponse({'Data':RoleAccessSerialize_data.data[0]['Role']})
                    RoleAccessdata = M_RoleAccess.objects.filter(Role=RoleAccessSerialize_data.data[0]['Role']).filter(
                        Company=RoleAccessSerialize_data.data[0]['Company']).filter(Division=RoleAccessSerialize_data.data[0]['Division'])
                    RoleAccessdata.delete()
                    RoleAccessSerialize_data.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Role Access Save Successfully', 'Data': []})
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': RoleAccessSerialize_data.errors, 'Data': []})
        except Exception :
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':   'Execution Error', 'Data': []})


class RoleAccessViewList(RetrieveAPIView):

    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    def get(self, request,id=0):
        try:
            with transaction.atomic():
                query = M_RoleAccess.objects.raw('''SELECT M_RoleAccess.id,M_RoleAccess.Role_id,M_Roles.Name RoleName,M_RoleAccess.Division_id,M_Parties.Name DivisionName,M_RoleAccess.Company_id,C_Companies.Name CompanyName
    FROM M_RoleAccess
    join M_Roles ON M_Roles.id=M_RoleAccess.Role_id
    left join M_Parties  ON M_Parties.id=M_RoleAccess.Division_id
    left join C_Companies  ON C_Companies.id=M_RoleAccess.Company_id  group by Role_id,Division_id,Company_id''')
                if not query:
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Records Not Found', 'Data': []})
                else:
                    M_Items_Serializer = M_RoleAccessSerializerGETList(
                        query, many=True).data
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': M_Items_Serializer})

        except Exception :
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  'Execution Error', 'Data': []})


class RoleAccessViewNewUpdated(RetrieveAPIView):

    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    def get(self, request,Role=0,Division=0):
        if int(Division) > 0:
            roleaccessquery = M_RoleAccess.objects.raw('''SELECT m_roleaccess.id id, h_modules.id moduleid, h_modules.Name ModuleName,m_pages.id pageid,m_pages.RelatedPageID, m_pages.name PageName  FROM m_roleaccess JOIN m_pages ON m_pages.id=m_roleaccess.Pages_id JOIN h_modules ON h_modules.id=m_roleaccess.Modules_id WHERE m_pages.PageType=2 AND Role_id=%s AND Division_id=%s   ''',([Role],[Division]))
        else:
            roleaccessquery = M_RoleAccess.objects.raw('''SELECT m_roleaccess.id id, h_modules.id moduleid, h_modules.Name ModuleName,m_pages.id pageid,m_pages.RelatedPageID, m_pages.name PageName  FROM m_roleaccess JOIN m_pages ON m_pages.id=m_roleaccess.Pages_id JOIN h_modules ON h_modules.id=m_roleaccess.Modules_id WHERE m_pages.PageType=2 AND Role_id=%s AND Division_id is null   ''',([Role]))            
        # return JsonResponse({'query':  str(roleaccessquery.query)})
        RoleAccessdata = M_RoleAccessSerializerNewUpdated(roleaccessquery, many=True).data
        # return JsonResponse({'data':  RoleAccessdata})
       
        Moduledata = list()

        for a in RoleAccessdata:
            id = a['id']
            pageid=a['pageid']
            RelatedPageID=a['RelatedPageID']

            if int(Division) > 0:
                RelatedPageroleaccessquery = M_RoleAccess.objects.raw('''SELECT m_roleaccess.id id,'a' as Name FROM m_roleaccess WHERE  Pages_id=%s and  Role_id=%s AND Division_id=%s    ''',([RelatedPageID],[Role],[Division]))
            else:
                RelatedPageroleaccessquery = M_RoleAccess.objects.raw('''SELECT m_roleaccess.id id,'a' as Name FROM m_roleaccess WHERE  Pages_id=%s and  Role_id=%s AND Division_id is null    ''',([RelatedPageID],[Role]))
            RelatedPageRoleAccessdata = MC_RolePageAccessSerializerNewUpdated(RelatedPageroleaccessquery, many=True).data
            # return JsonResponse({'data':  RelatedPageRoleAccessdata})
            
            rolepageaccessqueryforlistPage =  H_PageAccess.objects.raw('''SELECT h_pageaccess.Name,ifnull(mc_rolepageaccess.PageAccess_id,0) id from h_pageaccess left JOIN mc_rolepageaccess ON mc_rolepageaccess.PageAccess_id=h_pageaccess.id AND mc_rolepageaccess.RoleAccess_id=%s ''', [id])
            # # return JsonResponse({'query':  str(rolepageaccessquery.query)})
            RolePageAccessSerializerforListPAge = MC_RolePageAccessSerializerNewUpdated(rolepageaccessqueryforlistPage,  many=True).data
            # # return JsonResponse({'query':  RolePageAccessSerializerforListPAge})
            
            
            roleaccessID=RelatedPageRoleAccessdata[0]['id']
            rolepageaccessquery =  H_PageAccess.objects.raw('''SELECT h_pageaccess.Name,ifnull(mc_rolepageaccess.PageAccess_id,0) id from h_pageaccess left JOIN mc_rolepageaccess ON mc_rolepageaccess.PageAccess_id=h_pageaccess.id AND mc_rolepageaccess.RoleAccess_id=%s ''', [roleaccessID])
            # return JsonResponse({'query':  str(rolepageaccessquery.query)})
            RolePageAccessSerializer = MC_RolePageAccessSerializerNewUpdated(rolepageaccessquery,  many=True).data
            # return JsonResponse({'data':  RolePageAccessSerializer})
            pageaccessquery =  H_PageAccess.objects.raw('''SELECT h_pageaccess.Name,ifnull(mc_pagepageaccess.Access_id,0) id from h_pageaccess left JOIN mc_pagepageaccess ON mc_pagepageaccess.Access_id=h_pageaccess.id AND mc_pagepageaccess.Page_id=%s order by Sequence''', [pageid])
            # return JsonResponse({'query':  str(pageaccessquery.query)})
            PageAccessSerializer = M_PageAccessSerializerNewUpdated(pageaccessquery,  many=True).data
            Moduledata.append({
                "ModuleID": a['moduleid'],
                "ModuleName": a['ModuleName'],
                "PageID": a['pageid'],
                "RelatedPageID": a['RelatedPageID'],
                "PageName": a['PageName'],
                "RoleAccess_IsShowOnMenuForMaster": RolePageAccessSerializer[0]['id'],
                "RoleAccess_IsShowOnMenuForList": RolePageAccessSerializerforListPAge[0]['id'],
                "RoleAccess_IsSave": RolePageAccessSerializer[1]['id'],
                "RoleAccess_IsView": RolePageAccessSerializer[2]['id'],
                "RoleAccess_IsEdit": RolePageAccessSerializer[3]['id'],
                "RoleAccess_IsDelete": RolePageAccessSerializer[4]['id'],
                "RoleAccess_IsEditSelf": RolePageAccessSerializer[5]['id'],
                "RoleAccess_IsDeleteSelf": RolePageAccessSerializer[6]['id'],
                "RoleAccess_IsPrint": RolePageAccessSerializer[7]['id'],
                "RoleAccess_IsTopOfTheDivision": RolePageAccessSerializer[8]['id'],
                "RoleAccess_Pdfdownload": RolePageAccessSerializer[9]['id'],
                "RoleAccess_Exceldownload": RolePageAccessSerializer[10]['id'],
                "RoleAccess_IsCopy": RolePageAccessSerializer[11]['id'],
                "PageAccess_IsShowOnMenu": PageAccessSerializer[0]['id'],
                "PageAccess_IsSave": PageAccessSerializer[1]['id'],
                "PageAccess_IsView": PageAccessSerializer[2]['id'],
                "PageAccess_IsEdit": PageAccessSerializer[3]['id'],
                "PageAccess_IsDelete": PageAccessSerializer[4]['id'],
                "PageAccess_IsEditSelf": PageAccessSerializer[5]['id'],
                "PageAccess_IsDeleteSelf": PageAccessSerializer[6]['id'],
                "PageAccess_IsPrint": PageAccessSerializer[7]['id'],
                "PageAccess_IsTopOfTheDivision": PageAccessSerializer[8]['id'],
                "PageAccess_Pdfdownload": PageAccessSerializer[9]['id'],
                "PageAccess_Exceldownload": PageAccessSerializer[10]['id'],
                "PageAccess_IsCopy": PageAccessSerializer[11]['id'],

            })

        response = {
            "StatusCode": 200,
            "Status": True,
            "Message": " ",
            "Data": Moduledata,
        }
        return Response(response)

class RoleAccessViewAddPage(RetrieveAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    def get(self, request, pageid=0):
        roleaccessquery = M_Pages.objects.raw('''SELECT h_modules.id moduleid, h_modules.Name ModuleName,m_pages.id id,m_pages.RelatedPageID, m_pages.name PageName FROM m_pages JOIN h_modules ON h_modules.id=m_pages.Module_id WHERE m_pages.id=%s''',[pageid])
        # return JsonResponse({'query':  str(roleaccessquery.query)})
        RoleAccessdata = M_PageSerializerAddPage(roleaccessquery, many=True).data
        # return JsonResponse({'data':  RoleAccessdata})
        Moduledata = list()
        for a in RoleAccessdata:
            pageaccessquery =  H_PageAccess.objects.raw('''SELECT h_pageaccess.Name,ifnull(mc_pagepageaccess.Access_id,0) id from h_pageaccess left JOIN mc_pagepageaccess ON mc_pagepageaccess.Access_id=h_pageaccess.id AND mc_pagepageaccess.Page_id=%s order by Sequence''', [pageid])
            # return JsonResponse({'query':  str(pageaccessquery.query)})
            PageAccessSerializer = M_PageAccessSerializerAddPage(pageaccessquery,many=True).data
            Moduledata.append({
                "ModuleID": a['moduleid'],
                "ModuleName": a['ModuleName'],
                "PageID": a['id'],
                "RelatedPageID": a['RelatedPageID'],
                "PageName": a['PageName'],
                "RoleAccess_IsShowOnMenu": 0,
                "RoleAccess_IsSave": 0,
                "RoleAccess_IsView": 0,
                "RoleAccess_IsEdit": 0,
                "RoleAccess_IsDelete": 0,
                "RoleAccess_IsEditSelf": 0,
                "RoleAccess_IsDeleteSelf": 0,
                "RoleAccess_IsPrint": 0,
                "RoleAccess_IsTopOfTheDivision": 0,
                "RoleAccess_Pdfdownload": 0,
                "RoleAccess_Exceldownload": 0,
                "RoleAccess_IsCopy": 0,
                "PageAccess_IsShowOnMenu": PageAccessSerializer[0]['id'],
                "PageAccess_IsSave": PageAccessSerializer[1]['id'],
                "PageAccess_IsView": PageAccessSerializer[2]['id'],
                "PageAccess_IsEdit": PageAccessSerializer[3]['id'],
                "PageAccess_IsDelete": PageAccessSerializer[4]['id'],
                "PageAccess_IsEditSelf": PageAccessSerializer[5]['id'],
                "PageAccess_IsDeleteSelf": PageAccessSerializer[6]['id'],
                "PageAccess_IsPrint": PageAccessSerializer[7]['id'],
                "PageAccess_IsTopOfTheDivision": PageAccessSerializer[8]['id'],
                "PageAccess_Pdfdownload": PageAccessSerializer[9]['id'],
                "PageAccess_Exceldownload": PageAccessSerializer[10]['id'],
                "PageAccess_IsCopy": PageAccessSerializer[11]['id']
                   
            })

        response = {
            "StatusCode": 200,
            "Status": True,
            "Message": " ",
            "Data": Moduledata,
        }
        return Response(response)    

class RoleAccessGetPagesOnModule(RetrieveAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication
    
    def get(self, request, moduleid=0,Division=0):
        try:
            with transaction.atomic():
                
                if int(Division) > 0:
                    query = M_Pages.objects.raw('''Select m_pages.id,m_pages.Name FROM m_pages Join m_pagetype on m_pagetype.id= m_pages.PageType   WHERE m_pagetype.IsAvailableForAccess=1 and m_pages.IsDivisionRequired IN(1,0) and  Module_id=%s''',[moduleid])
                    
                else:
                    query = M_Pages.objects.raw('''Select m_pages.id,m_pages.Name FROM m_pages join m_pagetype on m_pagetype.id= m_pages.PageType  WHERE m_pagetype.IsAvailableForAccess=1  and m_pages.IsDivisionRequired=0 and Module_id=%s''',[moduleid])      
                   
                if not query:
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Records Not Found', 'Data': []})
                else:
                    PageSerializer = M_PageSerializerNewUpdated(
                        query, many=True).data
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': PageSerializer})
        except Exception  :
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  'Execution Error', 'Data': []})
        
      
class CopyRoleAccessView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):       
        Role = request.data['Role']
        Division  = request.data['Division']
        NewRole = request.data['NewRole']
        NewDivision = request.data['NewDivision']
        try:
            with transaction.atomic():
                if int(Division) > 0:
                    CopyRoleAccessdata = M_RoleAccess.objects.filter(Role_id= Role,Division_id =Division)
                else:
                    CopyRoleAccessdata = M_RoleAccess.objects.filter(Role_id= Role,Division_id__isnull=True)
                if CopyRoleAccessdata.exists():
                    serializersdata = CopyRoleAccessSerializer(CopyRoleAccessdata, many=True)
                    additionaldata=list()
                    for a in serializersdata.data:
                        if int(NewDivision) > 0:
                            a.update({'Role': NewRole,'Division':NewDivision})
                        else:   
                            a.update({'Role': NewRole,'Division':''})
                        additionaldata.append(a)
                    # return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  '0', 'Data':additionaldata})    
                    RoleAccessSerialize_data = InsertCopyRoleAccessSerializer(data=additionaldata, many=True)
                    if RoleAccessSerialize_data.is_valid():
                        # return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  '0', 'Data':RoleAccessSerialize_data.data}) 
                        RoleAccessdata = M_RoleAccess.objects.filter(Role=RoleAccessSerialize_data.data[0]['Role']).filter(
                            Company=RoleAccessSerialize_data.data[0]['Company']).filter(Division=RoleAccessSerialize_data.data[0]['Division'])
                        # return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  '0', 'Data':str(RoleAccessdata.query)}) 
                        RoleAccessdata.delete()
                        RoleAccessSerialize_data.save()
                    
                        return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Copy Role Access Save Successfully', 'Data': []})
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': RoleAccessSerialize_data.errors, 'Data': []})
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': 'Execution Error', 'Data': []})
        except Exception :
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':   'Execution Error', 'Data': []})