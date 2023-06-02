from ..models import *
from rest_framework import serializers

class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model =   M_States
        fields = '__all__'

class DistrictsSerializer(serializers.ModelSerializer):
    class Meta:
        model =   M_Districts
        fields = '__all__'

class CitiesSerializerSecond(serializers.ModelSerializer):
    class Meta:
        model =   M_Cities
        fields = '__all__'

class CitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model =   M_Cities
        fields = ['Name','District','CreatedBy','CreatedOn','UpdatedBy']
