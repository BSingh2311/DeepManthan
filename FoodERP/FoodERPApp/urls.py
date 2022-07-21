from django.urls import re_path as url

from .Views.V_Parties import *


from .Views.V_Orders import *

from .Views.V_Companies import *

from .Views.V_Pages import *

from .Views.V_Roles import *

from .Views.V_RoleAccess import *

from .Views.V_Modules import *

from .Views.V_PageAccess import *

from .Views.V_Login import *

from .Views.V_Items import *

from .Views.V_Invoices import *

from .Views.V_ItemsGroup import *

from .Views.V_Employees import *

from .Views.V_EmployeeTypes import *

from .Views.V_States import *

from .Views.V_Designations import *

from .Views.V_abc import * 


urlpatterns = [
    url(r'Registration', UserRegistrationView.as_view()),
    url(r'Login', UserLoginView.as_view()),
    url(r'ChangePassword', ChangePasswordView.as_view()),
    url(r'UserList/([0-9]+)$', UserListViewSecond.as_view()),
    url(r'UserList$', UserListView.as_view()),
    url(r'Modules/([0-9]+)$', H_ModulesViewSecond.as_view()),
    url(r'Modules$', H_ModulesView.as_view()),
    url(r'RoleAccess/([0-9]+)/([0-9]+)/([0-9]+)$', RoleAccessView.as_view()),
    url(r'RoleAccessList$', RoleAccessViewList.as_view()),
    url(r'PageMasterForRoleAccess/([0-9]+)$', PagesMasterForRoleAccessView.as_view()),
    url(r'Roles/([0-9]+)$', M_RolesViewSecond.as_view()),
    url(r'Roles$', M_RolesView.as_view()),
    url(r'PagesMaster/([0-9]+)$', M_PagesViewSecond.as_view()),
    url(r'PagesMaster$', M_PagesView.as_view()),
    url(r'showPagesListOnPageType$', showPagesListOnPageType.as_view()),
    url(r'PageAccess$', H_PageAccessView.as_view()),
    url(r'Company/([0-9]+)$', C_CompaniesViewSecond.as_view()),
    url(r'Company$', C_CompaniesView.as_view()),
    url(r'CompanyGroups/([0-9]+)$', C_CompanyGroupsViewSecond.as_view()),
    url(r'CompanyGroups$', C_CompanyGroupsView.as_view()),
    url(r'Orders/([0-9]+)$', T_OrdersViewSecond.as_view()),
    url(r'Orders$', T_OrdersView.as_view()),
    url(r'Designations/([0-9]+)$', M_DesignationsViewSecond.as_view()),
    url(r'Designations$',M_DesignationsView.as_view()),
    url(r'Items/([0-9]+)$', M_ItemsViewSecond.as_view()),
    url(r'Items$', M_ItemsView.as_view()),
    url(r'Employees/([0-9]+)$', M_EmployeesViewSecond.as_view()),
    url(r'Employees$', M_EmployeesView.as_view()),
    url(r'Invoices/([0-9]+)$', T_InvoicesViewSecond.as_view()),
    url(r'Invoices$', T_InvoiceView.as_view()),
    url(r'ItemGroups/([0-9]+)$', M_ItemsGroupViewSecond.as_view()),
    url(r'ItemGroups$', M_ItemsGroupView.as_view()),
    url(r'EmployeeTypes/([0-9]+)$', M_EmployeeTypeViewSecond.as_view()),
    url(r'EmployeeTypes$', M_EmployeeTypeView.as_view()),
    url(r'States$',M_StateView.as_view()),
    url(r'GetDistrictOnState/([0-9]+)$',M_DistrictView.as_view()), 
    url(r'Parties/([0-9]+)$', M_PartiesViewSecond.as_view()),
    url(r'Parties$', M_PartiesView.as_view()),
    url(r'DivisionTypes$', M_DivisionTypeView.as_view()),
    url(r'GetPartyTypeByDivisionTypeID/([0-9]+)$', GetPartyTypeByDivisionTypeID.as_view()),
    url(r'PartyTypes$', M_PartyTypeView.as_view()),
    url(r'demo$', AbcView.as_view()),
    url(r'RoleAccessNewUpdated/([0-9]+)/([0-9]+)$', RoleAccessViewNewUpdated.as_view()),
    
   
      
]
  

