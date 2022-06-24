from django.urls import re_path as url

from .Views.V_Parties import *


from .Views.V_Orders import *

from .Views.V_Companies import *

from .Views.V_Pages import *

from .Views.V_Roles import *

from .Views.V_RoleAccess import *

from .Views.V_Modules import *
# from  .Views.V_Login import UserLoginV iew

from .Views.V_PageAccess import *

from .Views.V_Login import *

from .Views.V_Items import *

from .Views.V_Invoices import *

from .Views.V_ItemsGroup import *

from .Views.V_Employees import *

from .Views.V_EmployeeTypes import *

from .Views.V_States import *

from .Views.V_Designations import *


urlpatterns = [
    url(r'Registration', UserRegistrationView.as_view()),
    url(r'Login', UserLoginView.as_view()),
    
    url(r'UserList/([0-9]+)$', UserListViewSecond.as_view()),
    url(r'UserList', UserListView.as_view()),
    
    url(r'Modules/([0-9]+)', H_ModulesViewSecond.as_view()),
    url(r'Modules$', H_ModulesView.as_view()),
    
    url(r'RoleAccess$', RoleAccessClass.as_view()),
    
    url(r'Roles/([0-9]+)$', M_RolesViewSecond.as_view()),
    url(r'Roles$', M_RolesView.as_view()),

    url(r'PagesMaster/([0-9]+)$', M_PagesViewSecond.as_view()),
    url(r'PagesMaster$', M_PagesView.as_view()),
    url(r'showPagesListOnPageType/([0-9]+)$', showPagesListOnPageType.as_view()),
    
    url(r'PageAccess$', H_PageAccessView.as_view()),
   

    url(r'Companies/([0-9]+)$', C_CompaniesViewSecond.as_view()),
    url(r'Companies$', C_CompaniesView.as_view()),

    url(r'CompanyGroups/([0-9]+)$', C_CompanyGroupsViewSecond.as_view()),
    url(r'CompanyGroups$', C_CompanyGroupsView.as_view()),

    # url(r'M_DivisionType/([0-9]+)$', M_DivisionTypeViewSecond.as_view()),
    # url(r'M_DivisionType$', M_DivisionTypeView.as_view()),
    
    url(r'Orders/([0-9]+)$', T_OrdersViewSecond.as_view()),
    url(r'Orders$', T_OrdersView.as_view()),
    url(r'Designations/([0-9]+)$', M_DesignationsViewSecond.as_view()),
    url(r'Designations$',M_DesignationsView.as_view()),
    url(r'Items/([0-9]+)$', M_ItemsViewSecond.as_view()),
    url(r'Items$', M_ItemsView.as_view()),
    url(r'Employees/([0-9]+)', M_EmployeesViewSecond.as_view()),
    url(r'Employees$', M_EmployeesView.as_view()),
    url(r'Invoices/([0-9]+)$', T_InvoicesViewSecond.as_view()),
    url(r'Invoices$', T_InvoiceView.as_view()),
    url(r'ItemGroup/([0-9]+)', M_ItemsGroupViewSecond.as_view()),
    url(r'ItemGroup$', M_ItemsGroupView.as_view()),
    url(r'EmployeeTypes/([0-9]+)$', M_EmployeeTypeViewSecond.as_view()),
    url(r'EmployeeTypes$', M_EmployeeTypeView.as_view()),
    url(r'States/([0-9]+)$', S_StateViewSecond.as_view()),
    url(r'States$',S_StateView.as_view()),
    url(r'M_Parties/([0-9]+)', M_PartiesViewSecond.as_view()),
    url(r'M_Parties$', M_PartiesView.as_view()),
    url(r'M_DivisionType$', M_DivisionTypeView.as_view()),
    url(r'GetPartyTypeByDivisionTypeID/([0-9]+)', GetPartyTypeByDivisionTypeID.as_view()),
    url(r'M_PartyType$', M_PartyTypeView.as_view()),
    
    
]
  

