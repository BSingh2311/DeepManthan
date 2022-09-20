from dataclasses import fields
from django.forms import SlugField
from rest_framework import serializers

from ..models import *

# Get ALL Method
class PriceListGETSerializer(serializers.ModelSerializer):
    class Meta:
        model =  M_PriceList
        fields = '__all__'
class C_CompanySerializer(serializers.ModelSerializer):
    class Meta :
        model= C_Companies
        fields = ['id','Name']

class PartyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model =  M_PartyType
        fields = ['id','Name']

class PriceListSerializer(serializers.ModelSerializer):
    
    Company = C_CompanySerializer()
    PLPartyType = PartyTypeSerializer()
    
    class Meta:
        model = M_PriceList
        fields = ['id', 'Name', 'BasePriceListID', 'Company', 'MkUpMkDn', 'PLPartyType', 'CreatedBy', 'CreatedOn', 'UpdatedBy', 'UpdatedOn']

class PriceListSerializer2(serializers.Serializer):
    id = serializers.IntegerField()
    Name = serializers.CharField(max_length=100)
    BasePriceListID = serializers.IntegerField()
    Company_id = serializers.IntegerField()
    CompanyName = serializers.CharField(max_length=100)
    MkUpMkDn = serializers.IntegerField()
    PLPartyType_id = serializers.IntegerField()
    PartyTypeName = serializers.CharField(max_length=100)
      