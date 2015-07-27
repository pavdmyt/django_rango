from rest_framework import serializers
from rango.models import Category, Page


class CatSerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('id', 'name', 'views', 'likes')


class PageSerializer(serializers.ModelSerializer):
    category = CatSerializer()

    class Meta:
        model = Page
        fields = ('category', 'id', 'title', 'url', 'views')
