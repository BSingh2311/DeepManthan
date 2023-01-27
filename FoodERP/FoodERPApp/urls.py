from django.urls import re_path as url

from .Views.V_Production import *

from .Views.V_GRNs import *

from .Views.V_Bom import *

from .Views.V_SuperAdmin import SuperAdminView

from .Views.V_Login import *

from .Views.V_Parties import *

from .Views.V_Orders import *

from .Views.V_Companies import *

from .Views.V_CompanyGroup import *

from .Views.V_Pages import *

from .Views.V_Roles import *

from .Views.V_RoleAccess import *

from .Views.V_Modules import *

from .Views.V_PageAccess import *

from .Views.V_WorkOrder import *

from .Views.V_Items import *

from .Views.V_Invoices import *

from .Views.V_Employees import *

from .Views.V_EmployeeTypes import *

from .Views.V_States import *

from .Views.V_Designations import *

from .Views.V_PriceLists import  *

from .Views.V_PartyTypes import *

from .Views.V_abc import * 

from .Views.V_SendMail import *

from .Views.V_CategoryType import *  

from .Views.V_Category import *

from .Views.V_GroupType import * 

from .Views.V_Group import * 

from .Views.V_SubGroup import *

from .Views.V_Units import * 

from .Views.V_Vehicles import *    

from .Views.V_Drivers import *

from .Views.V_VehicleTypes import *

from .Views.V_Mrps import *

from .Views.V_Margins import *

from .Views.V_GSTHSNCode import *

from .Views.V_PartySubParty import *

from .Views.V_PartyItems import *

from .Views.V_MaterialIssue import *

from .Views.V_TermsAndConditions import *

from .Views.V_GeneralMaster import *

from .Views.V_Demands import *

from .Views.V_InterbranchChallan import *

from .Views.V_InterBranchInward import *

urlpatterns = [
    
    # Master APIs IN Projects Add Page ,List Page
    url(r'test', AbcView.as_view()),
# User 
            url(r'Registration', UserRegistrationView.as_view()),
            url(r'Login', UserLoginView.as_view()),
            url(r'ChangePassword', ChangePasswordView.as_view()),
            url(r'UserList/([0-9]+)$', UserListViewSecond.as_view()),
            url(r'UserList$', UserListView.as_view()),
            #PartyDropdownforloginpage/EmployeeID
            # This below API used for Dropdown populated when user have multiple role and parties.
            url(r'PartyDropdownforloginpage/([0-9]+)$', UserPartiesForLoginPage.as_view()), 
            url(r'GetEmployeeForUserCreation$',GetEmployeeViewForUserCreation.as_view()),
            url(r'GetUserDetails$',GetUserDetailsView.as_view()),
            url(r'SuperAdmin$',SuperAdminView.as_view()),
            url(r'UserPartiesForUserMaster/([0-9]+)$', UserPartiesViewSecond.as_view()),
            url(r'SendMail$', SendViewMail.as_view()),
            url(r'VerifyOTP$', VerifyOTPwithUserData.as_view()),

# Modules 
            url(r'Modules/([0-9]+)$', H_ModulesViewSecond.as_view()),
            url(r'Modules$', H_ModulesView.as_view()),
    
# Roles
            url(r'Roles/([0-9]+)$', M_RolesViewSecond.as_view()),
            url(r'Roles$', M_RolesView.as_view()),
    
# PageMaster 
            url(r'PageMaster/([0-9]+)$', M_PagesViewSecond.as_view()),
            url(r'PageMaster$', M_PagesView.as_view()),
            url(r'PageTypeList$', M_PageTypeView.as_view()),
            url(r'PageAccess$', H_PageAccessView.as_view()),
            url(r'ControlTypes$', ControlTypeMasterView.as_view()),
            url(r'GetFieldValidationOnControlType/([0-9]+)$', FieldValidationsView.as_view()),
    
# Company 
            url(r'Company/([0-9]+)$', C_CompaniesViewSecond.as_view()),
            url(r'Company$', C_CompaniesView.as_view()),
            url(r'GetCompanyByDivisionTypeID/([0-9]+)$', GetCompanyByDivisionType.as_view()),
            url(r'GetCompanyByEmployeeType/([0-9]+)$', GetCompanyByEmployeeType.as_view()),
    
# CompanyGroups 
            url(r'CompanyGroups/([0-9]+)$', C_CompanyGroupViewSecond.as_view()),
            url(r'CompanyGroups$', C_CompanyGroupView.as_view()),
    
# Designations 
            url(r'Designations/([0-9]+)$', M_DesignationsViewSecond.as_view()),
            url(r'Designations$',M_DesignationsView.as_view()),
    
# Employees 
            url(r'Employees/([0-9]+)$', M_EmployeesViewSecond.as_view()),
            url(r'Employees$', M_EmployeesView.as_view()),
            url(r'EmployeeTypes/([0-9]+)$', M_EmployeeTypeViewSecond.as_view()),
            url(r'EmployeeTypes$', M_EmployeeTypeView.as_view()),
    
# Order All APIs
            url(r'TestOrderget/([0-9]+)$',TestOrdersView.as_view()),
            url(r'Orders/([0-9]+)$', T_OrdersViewSecond.as_view()),
            url(r'Orders$', T_OrdersView.as_view()),
            url(r'OrdersFilter$', OrderListFilterView.as_view()),
            # url(r'GetItemsForParty$',GetItemsForOrderView.as_view()),
            url(r'POType$',POTypeView.as_view()),
            url(r'OrderEdit$',EditOrderView.as_view()),

# Demands All APIs
            url(r'Demands/([0-9]+)$', DemandViewSecond.as_view()),
            url(r'Demands$', DemandView.as_view()),
            url(r'DemandsFilter$', DemandListFilterView.as_view()),
            url(r'InterBranches$', InterBranchDivisionView.as_view()),
            url(r'InterBranchesItems$', InterBranchItemsView.as_view()),


#InterBranch Challan  All APIs
            url(r'BranchInvoice/([0-9]+)$', InterBranchChallanViewSecond.as_view()),
            url(r'BranchInvoice$', InterBranchChallanView.as_view()),
            url(r'GetDemandDetails$', DemandDetailsForIBChallan.as_view()),
            url(r'BranchInvoiceFilter$', InterBranchChallanListFilterView.as_view()), 
            
#InterBranch Inward All APIs
            url(r'InterBranchInward/([0-9]+)$', InterBranchInwardViewSecond.as_view()),
            url(r'InterBranchInward$', InterBranchInwardView.as_view()),

            url(r'InterBranchInwardFilter$', InterBranchInwardListFilterView.as_view()),
            url(r'BranchInvoiceDetails/([0-9]+)$', BranchInvoiceDetailsView.as_view()),              

         

    
# TermsAndCondition All APIs
            url(r'TermsAndCondtions/([0-9]+)$', TermsAndCondtionsViewSecond.as_view()),
            url(r'TermsAndCondtions$', TermsAndCondtionsView.as_view()),



# General Master All APIs
            url(r'GeneralMaster/([0-9]+)$', GeneralMasterViewSecond.as_view()),
            url(r'GeneralMaster$', GeneralMasterView.as_view()),
            url(r'GeneralMasterList$', GeneralMasterFilterView.as_view()),
            url(r'GeneralMasterType$', GeneralMasterTypeView.as_view()),
            url(r'GeneralMasterSubType$', GeneralMasterSubTypeView.as_view()),

    
#Invoice All APIs
            url(r'Invoice/([0-9]+)$', InvoiceViewSecond.as_view()),
            url(r'Invoice$', InvoiceView.as_view()),
            url(r'GetOrderDetails$', OrderDetailsForInvoice.as_view()),
            url(r'InvoicesFilter$', InvoiceListFilterView.as_view()),
    
# GRN All API's
            url(r'MakeOrdersGrn$', GetOrderDetailsForGrnView.as_view()),
            url(r'GRN/([0-9]+)$',T_GRNViewSecond.as_view()),
            url(r'GRN$', T_GRNView.as_view()),
            url(r'GRNFilter$', GRNListFilterView.as_view()),
            
            
# Bill Of Material All API's
            url(r'Billofmaterial/([0-9]+)/([0-9]+)$',M_BOMsViewSecond.as_view()),
            url(r'Billofmaterial$', M_BOMsView.as_view()),
            url(r'BomFilter$', BOMListFilterView.as_view()),
    
# Work Order All API's
            url(r'BomDetails$', BomDetailsView.as_view()),
            url(r'WorkOrder/([0-9]+)$',WorkOrderViewSecond.as_view()),
            url(r'WorkOrder$', WorkOrderView.as_view()),
            url(r'WorkOrderFilter$', WorkOrderList.as_view()),
    
# Material Issues All API's
            url(r'WorkOrderDetails$', WorkOrderDetailsView.as_view()),
            url(r'MaterialIssue/([0-9]+)$',MaterialIssueViewSecond.as_view()),
            url(r'MaterialIssue$', MaterialIssueView.as_view()),
            url(r'MaterialIssueFilter$', MaterialIsssueList.as_view()),


#Production ALL API`s

            
            url(r'MaterialIssueDetails$',MaterialIssueDetailsView.as_view()),
            url(r'Production/([0-9]+)$',ProductionViewSecond.as_view()),
            url(r'Production$',ProductionView.as_view()),
            url(r'ProductionFilter$',ProductionList.as_view()),

# Parties=================================================================================
            url(r'States$',M_StateView.as_view()),
            url(r'Parties/([0-9]+)$', M_PartiesViewSecond.as_view()),
            url(r'Parties$', M_PartiesView.as_view()),
            url(r'Divisions/([0-9]+)$', DivisionsView.as_view()),
            url(r'PriceList/([0-9]+)$', PriceListViewSecond.as_view()),
            url(r'PriceList$', PriceListView.as_view()),
            url(r'PartyTypes/([0-9]+)$', PartyTypeViewSecond.as_view()),
            url(r'PartyTypes$', PartyTypeView.as_view()),
            url(r'ImageTypes$', M_ImageTypesView.as_view()),
           
            url(r'GetVendorSupplierCustomer$',GetVendorSupplierCustomerListView.as_view()),
            # url(r'GetSupplier/([0-9]+)$',GetSupplierListView.as_view()),
            # url(r'GetCustomer/([0-9]+)$',GetCustomerView.as_view()),
           
# State and District
            url(r'States$',M_StateView.as_view()),    
            url(r'GetDistrictOnState/([0-9]+)$',M_DistrictView.as_view()),

# PartySubParty
            url(r'PartySubParty/([0-9]+)$',PartySubPartyViewSecond.as_view()),
            url(r'PartySubParty$',PartySubPartyView.as_view()),

# Driver 
            url(r'Driver/([0-9]+)$', M_DriverViewSecond.as_view()),
            url(r'Driver$', M_DriverView.as_view()),
# Vehicle 
            url(r'VehicleTypes/([0-9]+)$', M_VehicleTypesViewSecond.as_view()),
            url(r'VehicleTypes$', M_VehicleTypesView.as_view()),
            url(r'Vehicle/([0-9]+)$', M_VehicleViewSecond.as_view()),
            url(r'Vehicle$', M_VehicleView.as_view()),    
    
#Item All APIs======================================================================================
            url(r'Items/([0-9]+)$', M_ItemsViewSecond.as_view()),
            url(r'Items$', M_ItemsView.as_view()),
            url(r'ItemTag$',M_ItemTag.as_view()),
            url(r'ItemBrand$',M_ItemBrandName.as_view()),
            url(r'MCUnitDetails$',MCUnitDetailsView.as_view()),
            # Select Item and Get MCItemUnits
            # url(r'GetItemUnits$',M_ItemsViewThird.as_view()),

# CategoryTypes
            url(r'CategoryTypes/([0-9]+)$', CategoryTypeViewSecond.as_view()),
            url(r'CategoryTypes$', CategoryTypeView.as_view()),
# Category
            url(r'Category/([0-9]+)$', CategoryViewSecond.as_view()),
            url(r'Category$', CategoryView.as_view()),
            url(r'GetCategoryByCategoryTypeID/([0-9]+)$', GetCategoryByCategoryTypeID.as_view()),
# GroupTypes
            url(r'GroupTypes/([0-9]+)$', GroupTypeViewSecond.as_view()),
            url(r'GroupTypes$', GroupTypeView.as_view()),
# Group
            url(r'Group/([0-9]+)$', GroupViewSecond.as_view()),
            url(r'Group$', GroupView.as_view()),
            url(r'GetGroupByGroupTypeID/([0-9]+)$', GetGroupByGroupTypeID.as_view()),
# SubGroups
            url(r'SubGroups/([0-9]+)$', SubGroupViewSecond.as_view()),
            url(r'SubGroups$', SubGroupView.as_view()),
            url(r'GetSubGroupByGroupID/([0-9]+)$', GetSubGroupByGroupID.as_view()),

# Unit 
            url(r'UnitList$', M_UnitsView.as_view()),

# PartyItemList
            url(r'PartyItemList/([0-9]+)$',PartyItemsViewSecond.as_view()),
            url(r'PartyItemList$',PartyItemsView.as_view()),
    
# Mrps
            url(r'Mrps$',M_MRPsView.as_view()),
            url(r'Mrps/([0-9]+)$',M_MRPsViewSecond.as_view()),
            url(r'DeleteMrpOnList/([0-9]+)$',M_MRPsViewThird.as_view()),
    
# Margins
            url(r'Margins$',M_MarginsView.as_view()),
            url(r'Margins/([0-9]+)$', M_MarginsViewSecond.as_view()),
            url(r'DeleteMarginOnList/([0-9]+)$', M_MarginsViewThird.as_view()),
    
# GstHsnCode 
            url(r'GstHsnCode$',M_GstHsnCodeView.as_view()),
            url(r'GstHsnCode/([0-9]+)$', M_GSTHSNCodeViewSecond.as_view()),
            url(r'DeleteGstHsnCodeOnList/([0-9]+)$', M_GSTHSNCodeViewThird.as_view()),
    
# GetMRP 
            url(r'GetMRP$',GETMrpDetails.as_view()),
            url(r'GetMargin$',GETMarginDetails.as_view()),
            url(r'GetGstHsncode$',GETGstHsnDetails.as_view()),
    
# RoleAccess========================================= 
            #SideMenu Partyid/Employeeid
            url(r'RoleAccess/([0-9]+)/([0-9]+)$', RoleAccessView.as_view()),
            #ListPage API 
            url(r'RoleAccessList$', RoleAccessViewList.as_view()),
            #Post Method API
            url(r'RoleAccess$', RoleAccessView.as_view()),
            #RoleAccess PAge Go button and Edit Button Roleid/Divisionid
            url(r'RoleAccessNewUpdated/([0-9]+)/([0-9]+)$', RoleAccessViewNewUpdated.as_view()),
            #RoleAccessGetPagesOnModule moduleid/Divisionid
            url(r'RoleAccessGetPages/([0-9]+)/([0-9]+)$', RoleAccessGetPagesOnModule.as_view()),
            #RoleAccess Page AddPage Button
            url(r'RoleAccessAddPage/([0-9]+)$', RoleAccessViewAddPage.as_view()),
    
            # Dependencies APIs IN Projects 
            url(r'showPagesListOnPageType$', showPagesListOnPageType.as_view()),
            url(r'PageMasterForRoleAccess/([0-9]+)$', PagesMasterForRoleAccessView.as_view()),
            url(r'CopyRoleAccessabc$',CopyRoleAccessView.as_view()),
            url(r'RegenrateToken$', RegenrateToken.as_view()),
    
     
]