from rest_framework import serializers
from .models import Category, House, Item, CustomUser
from rest_framework.fields import EmailField,CharField
from .utils import *

'''
Serializer : Python Object -> JSON

'''
class HouseSerializer(serializers.ModelSerializer):
    postcode = CharField(max_length=10)
    house_number = CharField(max_length=10)
    street = CharField(max_length=200)
    apartment_number = CharField(max_length=10,allow_blank=True)
    class Meta:
        model = House
        fields = ('postcode', 'house_number', "street","apartment_number")
    def validate(self, attrs):
        attrs = super().validate(attrs)
        '''
        TODO :
        More complex House validation logic
        '''
        google_fetched_data = fetch_house_info(street=attrs["street"],postcode=attrs["postcode"],house_number=attrs["house_number"],apartment_number=attrs["apartment_number"])
        try:
            existing_house = House.objects.get(place_id = google_fetched_data["place_id"]) 
            attrs["existing_house"] = existing_house
        except Exception:
            pass
        
        return attrs
    def create(self,validated_data):
        google_fetched_data= fetch_house_info(street = validated_data["street"],postcode = validated_data["postcode"],house_number = validated_data["house_number"],apartment_number = validated_data["apartment_number"])
        house = House.objects.create(**validated_data,**google_fetched_data)
        house.save()
        return house


class UserSerializer(serializers.ModelSerializer):

    house = HouseSerializer(required=True,many = False)
    class Meta:
        model = CustomUser
        fields = ("id","full_name", "email", "password","house")
        extra_kwargs = {'password': {'write_only': True}}
    

    def create(self, validated_data):
        print("Creating user : " , validated_data)
        house_data = validated_data.pop('house')
        print("House data: ", house_data)
        if "existing_house" in house_data:
            house = house_data.pop("existing_house")
        else:
            house = House.objects.create(**house_data)
            house.save()
    
        user = CustomUser.objects.create_user(**validated_data, house=house)
        user.save()
        return user


from django.contrib.auth import authenticate


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['category_id']

class ItemSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    categories = CategorySerializer(many= True,read_only =True)
    category_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    class Meta:
        model = Item
        fields = ['id', 'owner', 'price_per_day', 'title',"description",'categories', 'image',"date_added"]
        read_only_fields = ["owner"]
    def create(self, validated_data):
        # owner_data = validated_data.pop('owner')
        # owner, _ = CustomUser.objects.get(owner_data)
        category_ids = validated_data.pop('category_ids', [])

        item = Item.objects.create(**validated_data)
        categories = Category.objects.filter(category_id__in=category_ids)
        item.categories.set(categories)
        return item
    
class MarketItemSerializer(serializers.Serializer):
    # Django Rest Framework can automatically deal with single object inputed and a list of them, we don't need to modify the serializer
    owner_name = serializers.CharField(read_only=True)
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(read_only=True)
    price_per_day = serializers.FloatField(read_only=True)
    image_url = serializers.CharField(read_only=True)   
    distance = serializers.FloatField(read_only=True)
    
    



