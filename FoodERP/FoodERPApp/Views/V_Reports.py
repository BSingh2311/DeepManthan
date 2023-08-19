from datetime import datetime, timedelta
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from rest_framework.parsers import JSONParser

from ..Serializer.S_Parties import M_PartiesSerializerSecond

from ..Views.V_CommFunction import GetOpeningBalance, UnitwiseQuantityConversion
from ..Serializer.S_Invoices import InvoiceSerializerSecond

from ..Serializer.S_Reports import *
from ..models import *


class PartyLedgerReportView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, id=0):
        try:
            with transaction.atomic():

                Orderdata = JSONParser().parse(request)
                FromDate = Orderdata['FromDate']
                ToDate = Orderdata['ToDate']
                Customer = Orderdata['Customer']
                Party = Orderdata['Party']

                query = T_Invoices.objects.raw('''SELECT
    1 id,
    InvoiceDate,
    BillNo,
    BankName,
    BranchName,
    ChequeDate,
    DocumentNo,
    ReceiptMode,
    InvoiceAmount,
    TotalTCS,
    ReceiptAmt,
    CashReceiptAmt,
    DebitNote,
    CreditNote,
    Flag,
    BasicAmount,
    BA5,
    BA12,
    BA18,
    GA5,
    GA12,
    GA18,
    Description
FROM
    ((SELECT
        InvoiceDate,
            BillNo,
            BankName,
            BranchName,
            ChequeDate,
            DocumentNo,
            ReceiptMode,
            InvoiceAmount,
            TotalTCS,
            ReceiptAmt,
            CashReceiptAmt,
            Flag,
            DebitNote,
            CreditNote,

            BasicAmount,
            BA5,
            BA12,
            BA18,
            GA5,
            GA12,
            GA18,
            Description

    FROM
        (SELECT
        InvoiceDate,
            T_Invoices.id,
            FullInvoiceNumber BillNo,
            "" AS BankName,
            "" AS BranchName,
            "" AS ChequeDate,
            "" AS DocumentNo,
            "" AS ReceiptMode,
            GrandTotal InvoiceAmount,
            TCSAmount TotalTCS,
            0 AS ReceiptAmt,
            0 AS CashReceiptAmt,
            1 AS Flag,
            0 AS DebitNote,
            0 AS CreditNote,
            "" AS Description
    FROM
        T_Invoices
    WHERE
        InvoiceDate BETWEEN %s AND %s
            AND Party_id = %s
            AND Customer_id = %s) a
    LEFT JOIN (SELECT
        Invoice_id,
            SUM(BasicAmount) AS BasicAmount,

            SUM(CASE
                WHEN GSTPercentage = 5 THEN BasicAmount
                ELSE 0
            END) AS BA5,
            SUM(CASE
                WHEN GSTPercentage = 12 THEN BasicAmount
                ELSE 0
            END) AS BA12,
            SUM(CASE
                WHEN GSTPercentage = 18 THEN BasicAmount
                ELSE 0
            END) AS BA18,
            SUM(CASE
                WHEN GSTPercentage = 5 THEN GSTAmount
                ELSE 0
            END) AS GA5,
            SUM(CASE
                WHEN GSTPercentage = 12 THEN GSTAmount
                ELSE 0
            END) AS GA12,
            SUM(CASE
                WHEN GSTPercentage = 18 THEN GSTAmount
                ELSE 0
            END) AS GA18
    FROM
        TC_InvoiceItems
    GROUP BY Invoice_id) b ON a.id = b.Invoice_id)

    UNION
    SELECT
        ReceiptDate InvoiceDate,
            FullReceiptNumber BillNo,
            M_Bank.Name AS BankName,
            MC_PartyBanks.BranchName AS BranchName,
            ChequeDate ChequeDate,
            DocumentNo DocumentNo,
            M_GeneralMaster.Name AS ReceiptMode,
            0 AS InvoiceAmount,
            0 as TotalTCS,
            CASE
                WHEN ReceiptMode_id = 31 THEN 0
                ELSE AmountPaid
            END ReceiptAmt,
            CASE
                WHEN ReceiptMode_id = 31 THEN AmountPaid
                ELSE 0
            END CashReceiptAmt,
            2 AS Flag,
            0 AS DebitNote,
            0 AS CreditNote,
            0 AS BasicAmount,
            0 AS BA5,
            0 AS BA12,
            0 AS BA18,
            0 AS GA5,
            0 AS GA12,
            0 AS GA18,
            Description
    FROM
        T_Receipts
    LEFT JOIN MC_PartyBanks ON MC_PartyBanks.id = T_Receipts.Bank_id
    LEFT JOIN M_Bank ON M_Bank.id = MC_PartyBanks.Bank_id
    INNER JOIN M_GeneralMaster ON M_GeneralMaster.id = T_Receipts.ReceiptMode_id
    WHERE
        ReceiptDate BETWEEN %s AND %s
            AND T_Receipts.Party_id = %s
            AND T_Receipts.Customer_id = %s

            UNION
            SELECT
        CRDRNoteDate InvoiceDate,
            FullNoteNumber BillNo,
            "" AS BankName,
            "" AS BranchName,
            "" AS ChequeDate,
            "" AS DocumentNo,
            "" AS ReceiptMode,
            (CASE
                WHEN T_CreditDebitNotes.NoteType_id = 38 THEN T_CreditDebitNotes.GrandTotal
                ELSE 0
            END) AS InvoiceAmount,
            0 AS TotalTCS,
            (CASE
                WHEN T_CreditDebitNotes.NoteType_id = 38 THEN 0
                ELSE T_CreditDebitNotes.GrandTotal
            END) ReceiptAmt,
            0 AS CashReceiptAmt,
            (CASE
                WHEN T_CreditDebitNotes.NoteType_id = 38 THEN 3
                ELSE 4
            END) AS Flag,
            (CASE
                WHEN T_CreditDebitNotes.NoteType_id = 38 THEN T_CreditDebitNotes.GrandTotal
                ELSE 0
            END) AS DebitNote,
            (CASE
                WHEN T_CreditDebitNotes.NoteType_id = 38 THEN 0
                ELSE T_CreditDebitNotes.GrandTotal
            END) CreditNote,
            0 AS BasicAmount,
            0 AS BA5,
            0 AS BA12,
            0 AS BA18,
            0 AS GA5,
            0 AS GA12,
            0 AS GA18,
            "" AS Description
    FROM
        T_CreditDebitNotes
    WHERE
        T_CreditDebitNotes.CRDRNoteDate BETWEEN %s AND %s
            AND Party_id = %s
            AND Customer_id = %s) q
ORDER BY InvoiceDate , Flag , BillNo ''', [FromDate, ToDate, Party, Customer, FromDate, ToDate, Party, Customer, FromDate, ToDate, Party, Customer])

                if not query:
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Records Not Found', 'Data': []})
                else:
                    PartyLedgerSerializedata = PartyLedgerReportSerializer(
                        query, many=True).data
                    PartyLedgerData = list()
                    PartyLedgerItemDetails = list()
                    date_format = "%Y-%m-%d"

                    # Convert the string to a date object
                    date_object = datetime.strptime(
                        FromDate, date_format).date()
                    previous_date = date_object - timedelta(days=1)
                    Opening = GetOpeningBalance(Party, Customer, previous_date)
                    Closing = GetOpeningBalance(Party, Customer, ToDate)
                    temp = 0
                    TaxFreeSale = 0
                    TotalTaxableSale = 0
                    TaxableSale5 = 0
                    TaxableSale12 = 0
                    TaxableSale18 = 0
                    GSTAmount5 = 0
                    GSTAmount12 = 0
                    GSTAmount18 = 0
                    TotalCreditNote = 0
                    TotalDebitNote = 0
                    TotalTCS = 0
                    for a in PartyLedgerSerializedata:
                        if temp == 0:
                            temp = (float(Opening) + float(a['InvoiceAmount'])) - (
                                float(a['ReceiptAmt'])+float(a['CashReceiptAmt']))
                        else:
                            temp = (temp + float(a['InvoiceAmount'])) - \
                                    (float(a['ReceiptAmt']) +
                                     float(a['CashReceiptAmt']))

                        TaxFreeSale = 0.0
                        TotalTaxableSale = TotalTaxableSale + \
                            float(a["BasicAmount"])
                        TaxableSale5 = TaxableSale5 + float(a["BA5"])
                        TaxableSale12 = TaxableSale12 + float(a["BA12"])
                        TaxableSale18 = TaxableSale18 + float(a["BA18"])
                        GSTAmount5 = GSTAmount5 + float(a["GA5"])
                        GSTAmount12 = GSTAmount12 + float(a["GA12"])
                        GSTAmount18 = GSTAmount18 + float(a["GA18"])
                        TotalCreditNote = TotalCreditNote + \
                            float(a["CreditNote"])
                        TotalDebitNote = TotalDebitNote + float(a["DebitNote"])
                        TotalTCS = TotalTCS + float(a["TotalTCS"])
                        if a['BankName'] is None:
                            BankName = ''
                        else:
                            BankName = str(a['BankName'])
                        if a['BranchName'] is None:
                            BranchName = ''
                        else:
                            BranchName = str(a['BranchName'])
                        if a['DocumentNo'] is None:
                            DocumentNo = ''
                        else:
                            DocumentNo = str(a['DocumentNo'])
                        if a['ReceiptMode'] is None:
                            ReceiptMode = ''
                        else:
                            ReceiptMode = str(a['ReceiptMode'])

                        if a['Description'] is None or not a['Description']:

                            Description = ''
                        else:

                            Description = '(' + str(a['Description']) + ')'

                        print(BankName, '')
                        PartyLedgerItemDetails.append({
                            "Date": a['InvoiceDate'],
                            "DocumentNO": a['BillNo'],
                            "Particular": BankName+''+BranchName+''+DocumentNo+''+ReceiptMode + '' + Description,
                            "Amount": a['InvoiceAmount'],
                            "RecieptAmount": float(a['ReceiptAmt']) + float(a['CashReceiptAmt']),
                            "Cash": 0,
                            "Balance": float(temp),

                        })
                    q1 = M_Parties.objects.filter(
                        id=Party).values("Name", "PAN", "GSTIN")
                    q2 = M_Parties.objects.filter(
                        id=Customer).values("Name", "PAN", "GSTIN")
                    PartyLedgerData.append({
                        "FormDate": FromDate,
                        "ToDate": ToDate,
                        "Distributor": q1[0]['Name'],
                        "DistributorGSTIN": q1[0]["GSTIN"],
                        "DistributorPAN": q1[0]['PAN'],
                        "CustomerName": q2[0]['Name'],
                        "CustomerGSTIN":  q2[0]["GSTIN"],
                        "CustomerPAN": q2[0]["PAN"],
                        "Open": Opening,
                        "Close": Closing,
                        "TaxFreeSale": TaxFreeSale,
                        "TotalTaxableSale": TotalTaxableSale,
                        "TaxableSale5": TaxableSale5,
                        "TaxableSale12": TaxableSale12,
                        "TaxableSale18": TaxableSale18,
                        "GSTAmount5": GSTAmount5,
                        "GSTAmount12": GSTAmount12,
                        "GSTAmount18": GSTAmount18,
                        "TotalCreditNote": TotalCreditNote,
                        "TotalDebitNote": TotalDebitNote,
                        "TotalTCS": TotalTCS,
                        "InvoiceItems": PartyLedgerItemDetails
                    })
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': PartyLedgerData})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})



class GenericSaleView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, id=0):
        try:
            with transaction.atomic():
                Genericdata = JSONParser().parse(request)
                FromDate = Genericdata['FromDate']
                ToDate = Genericdata['ToDate']
                Party = Genericdata['Party']
                Party_list = Party.split(",")
                
        
                Genericdataquery = T_Invoices.objects.raw('''SELECT TC_InvoiceItems.id,T_Invoices.Party_id AS PartyID,A.Name PartyName,T_Invoices.FullInvoiceNumber,T_Invoices.InvoiceDate,T_Invoices.Customer_id AS CustomerID,B.Name CustomerName,M_Drivers.Name DriverName,M_Vehicles.VehicleNumber VehicleNo,TC_InvoiceItems.Item_id AS ItemID,M_Items.Name ItemName,C_Companies.Name CompanyName,M_GSTHSNCode.HSNCode,TC_InvoiceItems.MRPValue AS MRP,TC_InvoiceItems.QtyInNo,TC_InvoiceItems.QtyInKg,TC_InvoiceItems.QtyInBox,TC_InvoiceItems.Rate AS BasicRate,(TC_InvoiceItems.Rate + ((TC_InvoiceItems.Rate * TC_InvoiceItems.GSTPercentage) / 100)) WithGSTRate,M_Units.Name AS UnitName,TC_InvoiceItems.DiscountType,TC_InvoiceItems.Discount,TC_InvoiceItems.DiscountAmount,TC_InvoiceItems.BasicAmount AS TaxableValue,TC_InvoiceItems.CGST,TC_InvoiceItems.CGSTPercentage,TC_InvoiceItems.SGST,TC_InvoiceItems.SGSTPercentage,TC_InvoiceItems.IGST,TC_InvoiceItems.IGSTPercentage,TC_InvoiceItems.GSTPercentage,TC_InvoiceItems.GSTAmount,TC_InvoiceItems.Amount AS TotalValue,T_Orders.FullOrderNumber,T_Orders.OrderDate,T_Invoices.TCSAmount,T_Invoices.RoundOffAmount,T_Invoices.GrandTotal FROM TC_InvoiceItems JOIN T_Invoices ON T_Invoices.id = TC_InvoiceItems.Invoice_id JOIN TC_InvoicesReferences ON TC_InvoicesReferences.Invoice_id = T_Invoices.id JOIN T_Orders ON T_Orders.id = TC_InvoicesReferences.Order_id JOIN M_Parties A ON A.id = T_Invoices.Party_id JOIN M_Parties B ON B.id = T_Invoices.Customer_id JOIN M_Items ON M_Items.id = TC_InvoiceItems.Item_id JOIN C_Companies ON C_Companies.id = M_Items.Company_id JOIN M_GSTHSNCode ON M_GSTHSNCode.id = TC_InvoiceItems.GST_id JOIN MC_ItemUnits ON MC_ItemUnits.id = TC_InvoiceItems.Unit_id JOIN M_Units ON M_Units.id = MC_ItemUnits.UnitID_id JOIN MC_PartySubParty ON MC_PartySubParty.SubParty_id = T_Invoices.Customer_id AND MC_PartySubParty.Party_id IN %s LEFT JOIN M_Drivers ON M_Drivers.id = T_Invoices.Driver_id LEFT JOIN M_Vehicles ON M_Vehicles.id = T_Invoices.Vehicle_id WHERE T_Invoices.InvoiceDate BETWEEN %s AND %s AND T_Invoices.Party_id IN %s''',([Party_list,FromDate,ToDate,Party_list]))
                if Genericdataquery:
                    GenericSaleData=list()
                    GenericSaleSerializer=GenericSaleReportSerializer(Genericdataquery, many=True).data
                    GenericSaleData.append({"GenericSaleDetails" : GenericSaleSerializer})
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message':'', 'Data': GenericSaleData[0]})
                else:
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Records Not available ', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})


class RetailerDataView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, id=0):
        try:
            with transaction.atomic():
                Retailerdata = JSONParser().parse(request)
                Party = Retailerdata['Party']
                if(Party==0):
                    query = M_Parties.objects.raw('''SELECT M_Parties.id, Supplier.Name SupplierName,M_Parties.Name, M_Parties.isActive, M_Parties.Email, M_Parties.MobileNo, M_Parties.AlternateContactNo,MC_PartyAddress.Address,MC_PartyAddress.PIN,MC_PartyAddress.FSSAINo,MC_PartyAddress.FSSAIExipry,M_Parties.GSTIN, M_Parties.PAN,M_States.Name StateName,M_Districts.Name DistrictName,M_Cities.Name CityName,M_Routes.Name RouteName,C_Companies.Name CompanyName,M_PartyType.Name PartyTypeName, M_PriceList.Name PriceListName, M_Parties.Latitude, M_Parties.Longitude,M_Parties.SAPPartyCode
FROM MC_PartySubParty
JOIN M_Parties Supplier  ON Supplier.id= MC_PartySubParty.Party_id
JOIN M_Parties  ON M_Parties.id= MC_PartySubParty.SubParty_id
JOIN MC_PartyAddress ON MC_PartyAddress.Party_id =M_Parties.id AND  MC_PartyAddress.IsDefault=1
JOIN M_PartyType ON M_PartyType.id = M_Parties.PartyType_id AND M_PartyType.IsRetailer=1
JOIN M_States ON M_States.id = M_Parties.State_id
JOIN M_Districts ON M_Districts.id = M_Parties.District_id
LEFT JOIN M_Cities ON M_Cities.id=M_Parties.City_id
LEFT JOIN M_PriceList ON M_PriceList.id = M_Parties.PriceList_id
LEFT JOIN C_Companies ON C_Companies.id = M_Parties.Company_id
Left JOIN M_Routes ON M_Routes.id=MC_PartySubParty.Route_id
''')
                else:
                    query = M_Parties.objects.raw('''SELECT M_Parties.id, Supplier.Name SupplierName,M_Parties.Name, M_Parties.isActive, M_Parties.Email, M_Parties.MobileNo, M_Parties.AlternateContactNo,MC_PartyAddress.Address,MC_PartyAddress.PIN,MC_PartyAddress.FSSAINo,MC_PartyAddress.FSSAIExipry,M_Parties.GSTIN, M_Parties.PAN,M_States.Name StateName,M_Districts.Name DistrictName,M_Cities.Name CityName,M_Routes.Name RouteName,C_Companies.Name CompanyName,M_PartyType.Name PartyTypeName, M_PriceList.Name PriceListName, M_Parties.Latitude, M_Parties.Longitude,M_Parties.SAPPartyCode
FROM MC_PartySubParty
JOIN M_Parties Supplier  ON Supplier.id= MC_PartySubParty.Party_id
JOIN M_Parties  ON M_Parties.id= MC_PartySubParty.SubParty_id
JOIN MC_PartyAddress ON MC_PartyAddress.Party_id =M_Parties.id AND  MC_PartyAddress.IsDefault=1
JOIN M_PartyType ON M_PartyType.id = M_Parties.PartyType_id AND M_PartyType.IsRetailer=1
JOIN M_States ON M_States.id = M_Parties.State_id
JOIN M_Districts ON M_Districts.id = M_Parties.District_id
LEFT JOIN M_Cities ON M_Cities.id=M_Parties.City_id
LEFT JOIN M_PriceList ON M_PriceList.id = M_Parties.PriceList_id
LEFT JOIN C_Companies ON C_Companies.id = M_Parties.Company_id
Left JOIN M_Routes ON M_Routes.id=MC_PartySubParty.Route_id
WHERE MC_PartySubParty.Party_id=%s''',[Party])


               
                if query:
                    RetailerExportData=list()
                    RetailerExportSerializer=RetailerDataExportSerializer(query, many=True).data
                    RetailerExportData.append({"ReportExportSerializerDetails" : RetailerExportSerializer})
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message':'', 'Data': RetailerExportData[0]})
                else:
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Records Not available ', 'Data': []})  
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []}) 

# ================================Stock Processing ================================

class StockProcessingView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, id=0):
        try:
            with transaction.atomic():
                Orderdata = JSONParser().parse(request)
                start_date_str = Orderdata['FromDate']
                end_date_str = Orderdata['ToDate']
                Party = Orderdata['Party']
 
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
                
                date_range = []
                current_date = start_date
                while current_date <= end_date:
                    Date=current_date.strftime("%Y-%m-%d") 
                    print(Date)
                    # StockDeleteQuery  = O_DateWiseLiveStock.objects.raw('''DELETE FROM O_DateWiseLiveStock WHERE StockDate=%s AND Party_id=%s''',([Date],[Party]))
                    StockDeleteQuery  = O_DateWiseLiveStock.objects.filter(Party_id=Party,StockDate=Date)
                    StockDeleteQuery.delete()
                    # print(StockDeleteQuery.query)
                    StockProcessQuery = O_DateWiseLiveStock.objects.raw('''select id,ItemID,UnitID,round(OpeningBalance,3) OpeningBalance,round(GRN,3) GRN,round(SalesReturn,3) SalesReturn,round(Sale,3) Sale,round(PurchaseReturn,3) PurchaseReturn,
round(((OpeningBalance+GRN+SalesReturn)-(Sale+PurchaseReturn)),3) ClosingBalance
 from
(select 1 as id,I.Item_id ItemID,I.UnitID,
CASE WHEN StockQuantity >= 0  THEN IFNULL(StockQuantity,0)  ELSE IFNULL(ClosingBalance,0) END OpeningBalance,
IFNULL(InvoiveQuantity,0)Sale,IFNULL(GRNQuantity,0)GRN,IFNULL(SalesReturnQuantity,0)SalesReturn,IFNULL(PurchesReturnQuantity,0)PurchaseReturn

from
(Select Item_id,M_Items.BaseUnitID_id UnitID  from MC_PartyItems join M_Items on M_Items.id=MC_PartyItems.Item_id where Party_id=%s)I

left join
(SELECT IFNULL(Item_id,0) ItemID, sum(ClosingBalance)ClosingBalance FROM O_DateWiseLiveStock WHERE StockDate = DATE_SUB(  %s, INTERVAL 1 
					DAY ) AND Party_id =%s GROUP BY ItemID)CB
                    
on I.Item_id=CB.ItemID
left join
(SELECT Item_id,SUM(BaseUnitQuantity) GRNQuantity,SUM(Amount) GRNValue
FROM T_GRNs JOIN TC_GRNItems ON TC_GRNItems.GRN_id = T_GRNs.id
WHERE GRNDate = %s AND Customer_id = %s GROUP BY Item_id)GRN

on I.Item_id=GRN.Item_id
left join

(SELECT Item_id,SUM(BaseUnitQuantity) InvoiveQuantity,SUM(Amount) SaleValue
FROM T_Invoices JOIN TC_InvoiceItems ON TC_InvoiceItems.Invoice_id = T_Invoices.id
WHERE InvoiceDate = %s AND Party_id = %s GROUP BY Item_id)Invoice

on I.Item_id=Invoice.Item_id
left join

(SELECT Item_id,SUM(BaseUnitQuantity) StockQuantity
FROM T_Stock
WHERE StockDate = %s AND Party_id = %s GROUP BY Item_id)Stock

on I.Item_id=Stock.Item_id
left join

(SELECT Item_id,SUM(BaseUnitQuantity) SalesReturnQuantity,sum(Amount) SalesReturnValue
FROM T_PurchaseReturn join TC_PurchaseReturnItems on TC_PurchaseReturnItems.PurchaseReturn_id=T_PurchaseReturn.id      
WHERE ReturnDate = %s AND Party_id = %s GROUP BY Item_id)SalesReturn

on I.Item_id=SalesReturn.Item_id
left join

(SELECT Item_id,SUM(BaseUnitQuantity) PurchesReturnQuantity,sum(Amount) PurchesReturnValue   
FROM T_PurchaseReturn join TC_PurchaseReturnItems on TC_PurchaseReturnItems.PurchaseReturn_id=T_PurchaseReturn.id      
WHERE ReturnDate = %s AND Customer_id = %s GROUP BY Item_id)PurchesReturn
on I.Item_id=PurchesReturn.Item_id)R
where 
OpeningBalance!=0 OR GRN!=0 OR Sale!=0 OR PurchaseReturn != 0 OR SalesReturn !=0  ''',
([Party], [Date],[Party], [Date], [Party], [Date], [Party], [Date], [Party], [Date], [Party], [Date], [Party]))
                    
                    # print(StockProcessQuery)
                    serializer=StockProcessingReportSerializer(StockProcessQuery, many=True).data
                    # print(serializer)
                    for a in serializer:

                        stock=O_DateWiseLiveStock(StockDate=Date,OpeningBalance=a["OpeningBalance"], GRN=a["GRN"], Sale=a["Sale"], PurchaseReturn=a["PurchaseReturn"], SalesReturn=a["SalesReturn"], ClosingBalance=a["ClosingBalance"], ActualStock=0, Item_id=a["ItemID"], Unit_id=a["UnitID"], Party_id=Party, CreatedBy=0,  IsAdjusted=0, MRPValue=0)
                        stock.save()
                    current_date += timedelta(days=1)

                return JsonResponse({'StatusCode': 200, 'Status': True,'Message':'Stock Process Successfully', 'Data': []})

                


        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
        
# ======================================STOCK REPORT=================================

class StockReportView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, id=0):
        try:
            with transaction.atomic():

                Orderdata = JSONParser().parse(request)
                FromDate = Orderdata['FromDate']
                ToDate = Orderdata['ToDate']
                Unit = Orderdata['Unit']
                Party = Orderdata['Party']
                PartyNameQ=M_Parties.objects.filter(id=Party).values("Name")
                UnitName=M_Units.objects.filter(id=Unit).values("Name")
                unitname=UnitName[0]['Name']
                StockreportQuery=O_DateWiseLiveStock.objects.raw('''SELECT  1 as id,A.Item_id,A.Unit_id,
UnitwiseQuantityConversion(A.Item_id,ifnull(OpeningBalance,0),0,A.Unit_id,0,%s,0)OpeningBalance, 
UnitwiseQuantityConversion(A.Item_id,GRNInward,0,A.Unit_id,0,%s,0)GRNInward, 
UnitwiseQuantityConversion(A.Item_id,Sale,0,A.Unit_id,0,%s,0)Sale, 
UnitwiseQuantityConversion(A.Item_id,ClosingBalance,0,A.Unit_id,0,%s,0)ClosingBalance, 
UnitwiseQuantityConversion(A.Item_id,ActualStock,0,A.Unit_id,0,%s,0)ActualStock,
A.ItemName,
D.QuantityInBaseUnit,
UnitwiseQuantityConversion(A.Item_id,PurchaseReturn,0,A.Unit_id,0,%s,0)PurchaseReturn,
UnitwiseQuantityConversion(A.Item_id,SalesReturn,0,A.Unit_id,0,%s,0)SalesReturn
,GroupTypeName,GroupName,SubGroupName,%s UnitName
FROM 
	
	( SELECT M_Items.id Item_id, M_Items.Name ItemName ,Unit_id,M_Units.Name UnitName ,SUM(GRN) GRNInward, SUM(Sale) Sale, SUM(PurchaseReturn)PurchaseReturn,SUM(SalesReturn)SalesReturn,
    ifnull(M_GroupType.Name,'') GroupTypeName,ifnull(M_Group.Name,'') GroupName,ifnull(MC_SubGroup.Name,'') SubGroupName
	 FROM O_DateWiseLiveStock
	
	    JOIN M_Items ON M_Items.id=O_DateWiseLiveStock.Item_id 
        join M_Units on M_Units.id=O_DateWiseLiveStock.Unit_id
        left join MC_ItemGroupDetails on MC_ItemGroupDetails.Item_id=M_Items.id
		left JOIN M_GroupType ON M_GroupType.id = MC_ItemGroupDetails.GroupType_id 
		left JOIN M_Group ON M_Group.id  = MC_ItemGroupDetails.Group_id 
		left JOIN MC_SubGroup ON MC_SubGroup.id  = MC_ItemGroupDetails.SubGroup_id 
		 
		 WHERE StockDate BETWEEN %s AND %s AND Party_id=%s GROUP BY Item_id,M_GroupType.id,M_Group.id,MC_SubGroup.id) A 
		
		left JOIN (SELECT O_DateWiseLiveStock.Item_id, OpeningBalance FROM O_DateWiseLiveStock WHERE O_DateWiseLiveStock.StockDate = %s AND O_DateWiseLiveStock.Party_id=%s) B
		
		 ON A.Item_id = B.Item_id 
		
		 left JOIN (SELECT Item_id, ClosingBalance, ActualStock FROM O_DateWiseLiveStock WHERE StockDate = %s AND Party_id=%s) C
		 
		  ON A.Item_id = C.Item_id  
		
		LEFT JOIN (SELECT Item_id, SUM(BaseunitQuantity) QuantityInBaseUnit 
		FROM T_Stock 
		WHERE Party_id =%s AND StockDate BETWEEN %s AND %s 
		GROUP BY Item_id) D 		
		ON A.Item_id = D.Item_id ''',([Unit],[Unit],[Unit],[Unit],[Unit],[Unit],[Unit],[unitname],[FromDate],[ToDate],[Party],[FromDate],[Party],[ToDate],[Party],[Party],[FromDate],[ToDate]))
                print(StockreportQuery)
                serializer=StockReportSerializer(StockreportQuery, many=True).data
                
                
                StockData=list()
                StockData.append({
                            
                            "FromDate" : FromDate,
                            "ToDate" : ToDate,
                            "PartyName": PartyNameQ[0]["Name"],
                            "StockDetails" : serializer
                            
                })
                
            if StockData:
                if ['StatusCode'] == 200:  
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': StockData})      
                else:
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Record Not Found', 'Data': []})           
            else:
                return JsonResponse({'StatusCode': 204, 'Status': False, 'Message': 'Record Not Found', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
                                          
         
# select I.Item_id,I.ItemName,InvoiveQuantity,InvoiceMRP,GRNQuantity,GRNMRP,StockQuantity,StockMRP,SalesReturnQuantity,SalesReturnMRP,PurchesReturnQuantity,PurchesReturnMRP from 

# (Select Item_id ,M_Items.Name ItemName from MC_PartyItems join M_Items on M_Items.id=MC_PartyItems.Item_id where Party_id=14)I

# left join
# (SELECT 
#     Item_id,
#     MRPValue GRNMRP,
#     SUM(BaseUnitQuantity) GRNQuantity,
#     SUM(Amount) GRNValue
# FROM
#     T_GRNs
#         JOIN
#     TC_GRNItems ON TC_GRNItems.GRN_id = T_GRNs.id
# WHERE
#     GRNDate = '2023-07-21' AND Customer_id = 14
# GROUP BY Item_id,MRPValue)b


# on I.Item_id=b.Item_id

# left join
# (SELECT 
#     Item_id,
#     MRPValue InvoiceMRP,
#     SUM(BaseUnitQuantity) InvoiveQuantity,
#     SUM(Amount) SaleValue
# FROM
#     T_Invoices
#         JOIN
#     TC_InvoiceItems ON TC_InvoiceItems.Invoice_id = T_Invoices.id
# WHERE
#     InvoiceDate = '2023-07-21'AND Party_id = 14
# GROUP BY Item_id,MRPValue)a
# on I.Item_id=a.Item_id  and b.GRNMRP=a.InvoiceMRP
# left join


# (SELECT 
#     Item_id,
#     MRPValue StockMRP,
#     SUM(BaseUnitQuantity) StockQuantity
# FROM
#     T_Stock
# WHERE
#     StockDate = '2023-07-21' AND Party_id = 14
# GROUP BY Item_id,MRPValue)c

# on I.Item_id=c.Item_id and b.GRNMRP=c.StockMRP
# left join

# (SELECT 
#     Item_id,
#     MRPValue SalesReturnMRP,
#     SUM(BaseUnitQuantity) SalesReturnQuantity,
#     sum(Amount) SalesReturnValue
# FROM
#     T_PurchaseReturn
#     join TC_PurchaseReturnItems on TC_PurchaseReturnItems.PurchaseReturn_id=T_PurchaseReturn.id   
# WHERE
#     ReturnDate = '2023-07-21' AND Party_id = 14
# GROUP BY Item_id,MRPValue)d

# on I.Item_id=d.Item_id and b.GRNMRP=d.SalesReturnMRP
# left join
# (SELECT 
#     Item_id,
#     MRPValue PurchesReturnMRP,
#     SUM(BaseUnitQuantity) PurchesReturnQuantity,
#     sum(Amount) PurchesReturnValue
# FROM
#     T_PurchaseReturn
#     join TC_PurchaseReturnItems on TC_PurchaseReturnItems.PurchaseReturn_id=T_PurchaseReturn.id   
# WHERE
#     ReturnDate = '2023-07-21' AND Customer_id = 14
# GROUP BY Item_id,MRPValue)e
# on I.Item_id=e.Item_id and b.GRNMRP=e.PurchesReturnMRP

class PurchaseGSTReportView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    
    def post(self, request, id=0):
        try:
            with transaction.atomic():
                Reportdata = JSONParser().parse(request)
                FromDate = Reportdata['FromDate']
                ToDate = Reportdata['ToDate']
                Customer =  Reportdata['Party']
                GSTRatewise = Reportdata['GSTRatewise']
                
                if GSTRatewise == 1:
                   
                    query = TC_GRNReferences.objects.raw('''SELECT 1 As id, GSTPercentage,  SUM(BasicAmount) TaxableValue, SUM(CGST) CGST, SUM( SGST) SGST, SUM( IGST) IGST, SUM(GSTAmount) GSTAmount, SUM(Amount) TotalValue   FROM TC_GRNReferences JOIN T_Invoices ON T_Invoices.id =TC_GRNReferences.Invoice_id JOIN TC_InvoiceItems ON TC_InvoiceItems.Invoice_id = T_Invoices.id WHERE T_Invoices.InvoiceDate BETWEEN %s AND %s AND T_Invoices.Customer_id= %s GROUP BY TC_InvoiceItems.GSTPercentage''',([FromDate],[ToDate],[Customer]))
                    if query :
                        PurchaseGSTRateWiseData=list()
                        PurchaseGSTRateWiseSerializer=PurchaseGSTRateWiseReportSerializer(query, many=True).data
                        PurchaseGSTRateWiseData.append({"PurchaseGSTRateWiseDetails" : PurchaseGSTRateWiseSerializer})
                        return JsonResponse({'StatusCode': 200, 'Status': True,'Message':'', 'Data': PurchaseGSTRateWiseData[0]})
                    else:
                        return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Records Not available ', 'Data': []})
                else:
                    query=TC_GRNReferences.objects.raw('''SELECT 1 AS id,M_Parties.Name,InvoiceNumber,FullInvoiceNumber,InvoiceDate,SUM(CGSTPercentage + SGSTPercentage + IGSTPercentage) GSTRate,GSTPercentage,SUM(BasicAmount) TaxableValue,SUM(CGST) CGST,SUM(SGST) SGST,SUM(IGST) IGST,SUM(GSTAmount) GSTAmount,SUM(TC_InvoiceItems.DiscountAmount) DiscountAmount,SUM(Amount) TotalValue FROM TC_GRNReferences JOIN T_Invoices ON T_Invoices.id = TC_GRNReferences.Invoice_id JOIN TC_InvoiceItems ON TC_InvoiceItems.Invoice_id = T_Invoices.id JOIN M_Parties ON T_Invoices.Party_id = M_Parties.id WHERE T_Invoices.InvoiceDate BETWEEN %s AND %s AND T_Invoices.Customer_id =%s GROUP BY M_Parties.id, T_Invoices.InvoiceNumber, T_Invoices.FullInvoiceNumber, T_Invoices.InvoiceDate, TC_InvoiceItems.GSTPercentage''',([FromDate],[ToDate],[Customer]))
                    if query :
                        PurchaseGSTSerializer= PurchaseGSTReportSerializer(query, many=True).data
                        # print(PurchaseGSTSerializer)
                        PurchaseGSTData=list()
                        PurchaseGSTData.append({"PurchaseGSTDetails" : PurchaseGSTSerializer})
                        return JsonResponse({'StatusCode': 200, 'Status': True,'Message':'', 'Data': PurchaseGSTData[0]})
                    else:
                        return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Records Not available ', 'Data': []})  
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
  
  
        
class InvoiceDateExportReportView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    def post(self, request, id=0):
        try:
            with transaction.atomic():
                Reportdata = JSONParser().parse(request)
                FromDate = Reportdata['FromDate']
                ToDate = Reportdata['ToDate']
                Party =  Reportdata['Party']
           
                query = T_Invoices.objects.raw('''SELECT TC_InvoiceItems.id,T_Invoices.Party_id AS SupplierID,A.Name SupplierName,T_Invoices.FullInvoiceNumber As InvoiceNumber,T_Invoices.InvoiceDate,T_Invoices.Customer_id As CustomerID,B.Name CustomerName,TC_InvoiceItems.Item_id AS FE2MaterialID,M_Items.Name As MaterialName,C_Companies.Name CompanyName,M_GSTHSNCode.HSNCode,TC_InvoiceItems.MRPValue AS MRP,TC_InvoiceItems.QtyInNo,TC_InvoiceItems.QtyInKg,TC_InvoiceItems.QtyInBox,TC_InvoiceItems.Rate AS BasicRate,(TC_InvoiceItems.Rate +((TC_InvoiceItems.Rate * TC_InvoiceItems.GSTPercentage)/100))WithGSTRate, M_Units.Name AS UnitName,TC_InvoiceItems.DiscountType, TC_InvoiceItems.Discount,TC_InvoiceItems.DiscountAmount,TC_InvoiceItems.BasicAmount As TaxableValue,TC_InvoiceItems.CGST,TC_InvoiceItems.CGSTPercentage,TC_InvoiceItems.SGST,TC_InvoiceItems.SGSTPercentage,TC_InvoiceItems.IGST,TC_InvoiceItems.IGSTPercentage,TC_InvoiceItems.GSTPercentage,TC_InvoiceItems.GSTAmount,TC_InvoiceItems.Amount AS TotalValue,T_Invoices.TCSAmount,T_Invoices.RoundOffAmount,T_Invoices.GrandTotal,M_Routes.Name AS RouteName,M_States.Name AS StateName,B.GSTIN,TC_InvoiceUploads.Irn, TC_InvoiceUploads.AckNo,TC_InvoiceUploads.EwayBillNo
FROM TC_InvoiceItems
JOIN T_Invoices ON T_Invoices.id =TC_InvoiceItems.Invoice_id
JOIN TC_InvoicesReferences ON TC_InvoicesReferences.Invoice_id=T_Invoices.id
JOIN T_Orders ON T_Orders.id = TC_InvoicesReferences.Order_id
JOIN M_Parties A ON A.id= T_Invoices.Party_id
JOIN M_Parties B ON B.id = T_Invoices.Customer_id
JOIN M_States ON M_States.id = B.State_id
JOIN M_Items ON M_Items.id = TC_InvoiceItems.Item_id
JOIN C_Companies ON C_Companies.id = M_Items.Company_id
JOIN M_GSTHSNCode ON M_GSTHSNCode.id=TC_InvoiceItems.GST_id
JOIN MC_ItemUnits ON MC_ItemUnits.id=TC_InvoiceItems.Unit_id
JOIN M_Units ON M_Units.id = MC_ItemUnits.UnitID_id
JOIN MC_PartySubParty ON MC_PartySubParty.SubParty_id=T_Invoices.Customer_id AND MC_PartySubParty.Party_id=%s
LEFT JOIN M_Routes ON M_Routes.id=MC_PartySubParty.Route_id
LEFT JOIN TC_InvoiceUploads on TC_InvoiceUploads.Invoice_id = T_Invoices.id
WHERE T_Invoices.InvoiceDate BETWEEN %s AND %s AND  T_Invoices.Party_id=%s ''',([Party],[FromDate],[ToDate],[Party]))
                # print(str(query.query))
                if query:
                    InvoiceExportData=list()
                    InvoiceExportSerializer=InvoiceDataExportSerializer(query, many=True).data
                    InvoiceExportData.append({"InvoiceExportSerializerDetails" : InvoiceExportSerializer})
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message':'', 'Data': InvoiceExportData[0]})
                else:
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Records Not available ', 'Data': []})  
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []}) 
        
        
class DeletedInvoiceDateExportReportView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    def post(self, request, id=0):
        try:
            with transaction.atomic():
                Reportdata = JSONParser().parse(request)
                FromDate = Reportdata['FromDate']
                ToDate = Reportdata['ToDate']
                Party =  Reportdata['Party']
                query = T_DeletedInvoices.objects.raw('''SELECT TC_DeletedInvoiceItems.id,T_DeletedInvoices.Party AS SupplierID,A.Name SupplierName,T_DeletedInvoices.FullInvoiceNumber As InvoiceNumber,T_DeletedInvoices.InvoiceDate,T_DeletedInvoices.Customer As CustomerID,B.Name CustomerName,TC_DeletedInvoiceItems.Item AS FE2MaterialID,M_Items.Name As MaterialName,C_Companies.Name CompanyName,M_GSTHSNCode.HSNCode,TC_DeletedInvoiceItems.MRPValue AS MRP,TC_DeletedInvoiceItems.QtyInNo,TC_DeletedInvoiceItems.QtyInKg,TC_DeletedInvoiceItems.QtyInBox,TC_DeletedInvoiceItems.Rate AS BasicRate,(TC_DeletedInvoiceItems.Rate +((TC_DeletedInvoiceItems.Rate * TC_DeletedInvoiceItems.GSTPercentage)/100))WithGSTRate, M_Units.Name AS UnitName,TC_DeletedInvoiceItems.DiscountType, TC_DeletedInvoiceItems.Discount,TC_DeletedInvoiceItems.DiscountAmount,TC_DeletedInvoiceItems.BasicAmount As TaxableValue,TC_DeletedInvoiceItems.CGST,TC_DeletedInvoiceItems.CGSTPercentage,TC_DeletedInvoiceItems.SGST,TC_DeletedInvoiceItems.SGSTPercentage,TC_DeletedInvoiceItems.IGST,TC_DeletedInvoiceItems.IGSTPercentage,TC_DeletedInvoiceItems.GSTPercentage,TC_DeletedInvoiceItems.GSTAmount,TC_DeletedInvoiceItems.Amount AS TotalValue,T_DeletedInvoices.TCSAmount,T_DeletedInvoices.RoundOffAmount,T_DeletedInvoices.GrandTotal,M_Routes.Name AS RouteName,M_States.Name AS StateName,B.GSTIN,TC_DeletedInvoiceUploads.Irn, TC_DeletedInvoiceUploads.AckNo,TC_DeletedInvoiceUploads.EwayBillNo
FROM TC_DeletedInvoiceItems
JOIN T_DeletedInvoices ON T_DeletedInvoices.Invoice =TC_DeletedInvoiceItems.Invoice
JOIN M_Parties A ON A.id= T_DeletedInvoices.Party
JOIN M_Parties B ON B.id = T_DeletedInvoices.Customer
JOIN M_States ON M_States.id = B.State_id
JOIN M_Items ON M_Items.id = TC_DeletedInvoiceItems.Item
JOIN C_Companies ON C_Companies.id = M_Items.Company_id
JOIN M_GSTHSNCode ON M_GSTHSNCode.id=TC_DeletedInvoiceItems.GST
JOIN MC_ItemUnits ON MC_ItemUnits.id=TC_DeletedInvoiceItems.Unit
JOIN M_Units ON M_Units.id = MC_ItemUnits.UnitID_id
JOIN MC_PartySubParty ON MC_PartySubParty.SubParty_id=T_DeletedInvoices.Customer AND MC_PartySubParty.Party_id=%s
LEFT JOIN M_Routes ON M_Routes.id=MC_PartySubParty.Route_id
LEFT JOIN TC_DeletedInvoiceUploads on TC_DeletedInvoiceUploads.Invoice= T_DeletedInvoices.id
WHERE T_DeletedInvoices.InvoiceDate BETWEEN %s AND %s AND  T_DeletedInvoices.Party=%s ''',([Party],[FromDate],[ToDate],[Party]))
                print(str(query.query))
                if query:
                    DeletedInvoiceExportData=list()
                    DeletedInvoiceExportSerializer=InvoiceDataExportSerializer(query, many=True).data
                    DeletedInvoiceExportData.append({"DeletedInvoiceExportSerializerDetails" : DeletedInvoiceExportSerializer})
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message':'', 'Data': DeletedInvoiceExportData[0]})
                else:
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Records Not available ', 'Data': []})  
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})         
        

class StockDamageReportView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            with transaction.atomic():
                Damagedata = JSONParser().parse(request)
                FromDate = Damagedata['FromDate']
                ToDate = Damagedata['ToDate']
                PartyID = Damagedata['PartyID']
                ConversionUnit = Damagedata['Unit']

                query1 = M_Units.objects.filter(
                    id=ConversionUnit).values('Name')
                query = O_BatchWiseLiveStock.objects.raw(
                    '''SELECT M_Items.id, M_Items.Name ItemName, SUM(BaseUnitQuantity) Qty,M_Units.id UnitID FROM O_BatchWiseLiveStock JOIN M_Items ON M_Items.id=O_BatchWiseLiveStock.Item_id JOIN M_Units ON M_Units.id=M_Items.BaseUnitID_id  WHERE O_BatchWiseLiveStock.Party_id=%s AND O_BatchWiseLiveStock.IsDamagePieces=1 AND O_BatchWiseLiveStock.BaseUnitQuantity>0   GROUP BY O_BatchWiseLiveStock.Item_id''', ([PartyID]))
                if query:
                    DamageStockData = list()
                    DamageItemStocktSerializer = DamageStocktSerializer(
                        query, many=True).data
                    for a in DamageItemStocktSerializer:
                        ConversionUnitQty = UnitwiseQuantityConversion(
                            a['id'], a['Qty'], 0, a['UnitID'], 0, ConversionUnit, 0).ConvertintoSelectedUnit()
                        DamageStockData.append({
                            "id": a['id'],
                            "ItemName": a['ItemName'],
                            "Quantity": ConversionUnitQty,
                            "UnitName": query1[0]['Name']
                        })

                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': DamageStockData})
                else:
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Records Not available ', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

    
                                            
                                 