from rest_framework import serializers
from api.models import Order, OrderItem

class OrderItemSerializer_2(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.title")
    product_image = serializers.CharField(source="product.image")
    seller_name = serializers.CharField(source="product.seller.username")
    order_item_total_price = serializers.SerializerMethodField()
    created_at = serializers.CharField(source="order.created_at")
    buyer_name = serializers.CharField(source="order.user.username")
    class Meta:
        model = OrderItem
        fields = ["product_name","id","seller_name","created_at","quantity","status", "order_item_total_price","product_image","buyer_name"]
 
    def get_order_item_total_price(self, obj): 
        return obj.total_price()
 
class OrderSerializer_2(serializers.ModelSerializer):
    order_id = serializers.IntegerField(source="id")
    order_total = serializers.SerializerMethodField()
    orderitems = OrderItemSerializer_2(source="order_items", many=True)

    class Meta:
        model = Order 
        fields = ["order_id", "order_total", "orderitems","created_at"]

    def get_order_total(self, obj):
        return sum(item.total_price() for item in obj.order_items.all())
