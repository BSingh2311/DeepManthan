from rest_framework import serializers
from ..models import *
from ..Serializer.S_Drivers import  *
from ..Serializer.S_Vehicles import  *
from ..Serializer.S_Routes import  *
from ..Serializer.S_Parties import  *

class LoadingSheetListSerializer(serializers.ModelSerializer):
    Party = M_PartiesSerializerSecond()
    Route = RouteSerializer()
    Driver = M_DriverSerializer()
    Vehicle = VehiclesSerializerSecond()
    class Meta:
        model = T_LoadingSheet
        fields = ['id', 'Date', 'No', 'Party', 'Route','TotalAmount', 'InvoiceCount', 'Vehicle', 'Driver', 'CreatedBy', 'UpdatedBy','CreatedOn', 'LoadingSheetDetails']

# Post and Put Methods Serializer

class LoadingSheetDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model =  TC_LoadingSheetDetails
        fields = ['Invoice']

class LoadingSheetSerializer(serializers.ModelSerializer):
    LoadingSheetDetails = LoadingSheetDetailsSerializer(many=True)
    class Meta:
        model = T_LoadingSheet
        fields = ['id', 'Date', 'No', 'Party', 'Route','TotalAmount', 'InvoiceCount', 'Vehicle', 'Driver', 'CreatedBy', 'UpdatedBy','CreatedOn', 'LoadingSheetDetails']
        
    def create(self, validated_data):
        LoadingSheetDetails_data = validated_data.pop('LoadingSheetDetails')
        LoadingSheetID = T_LoadingSheet.objects.create(**validated_data)
        for LoadingSheet_data in LoadingSheetDetails_data:
            TC_LoadingSheetDetails.objects.create(LoadingSheet=LoadingSheetID, **LoadingSheet_data)
            print(LoadingSheet_data['Invoice'])
            print(validated_data[0]['Vehicle'])
            print(validated_data[0]['Driver'])
            # InvoiceVehicleandDriverupdate=T_Invoices.objects.filter(id=LoadingSheet_data['Invoice']).update(Vehicle = validated_data[0]['Vehicle'],Driver = validated_data[0]['Driver'])
            
            
        return LoadingSheetID 
       

class LoadingSheetInvoicesSerializer(serializers.Serializer):
    
    id = serializers.IntegerField()
    InvoiceDate = serializers.DateField()
    Customer_id = serializers.IntegerField()
    FullInvoiceNumber =  serializers.CharField(max_length=500)
    GrandTotal = serializers.CharField(max_length=500)
    Party_id =  serializers.IntegerField()
    CreatedOn = serializers.CharField(max_length=500)
    UpdatedOn = serializers.EmailField(max_length=200)
    Name = serializers.CharField(max_length=500)
         
        
        