from rest_framework import serializers
from .models import CustomUser, Enquiry, Wishlist, Cart, CartProduct, Order, OrderItem, Product
from django.contrib.auth import get_user_model
from rest_framework import serializers, status


CustomUser = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'phone_number', 'password', 'is_seller', 'is_buyer', 'pincode', 'district', 'location', 'date_of_birth', 'company_name', 'company_address', 'gstin', 'language')

    def validate(self, attrs):
        is_seller = attrs.get('is_seller', False)
        is_buyer = attrs.get('is_buyer', False)

        if not is_seller and not is_buyer:
            raise serializers.ValidationError("User must be either a seller or a buyer.")

        if is_seller:
            if not all([attrs.get('company_name'), attrs.get('company_address'), attrs.get('gstin')]):
                raise serializers.ValidationError("Sellers must provide company details.")

        return attrs

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            phone_number=validated_data['phone_number'],
            password=validated_data['password'],
            is_seller=validated_data.get('is_seller', False),
            is_buyer=validated_data.get('is_buyer', False),
            pincode=validated_data.get('pincode', "000000"),
            district=validated_data.get('district', "Unknown District"),
            location=validated_data.get('location', ""),
            date_of_birth=validated_data.get('date_of_birth'),
            company_name=validated_data.get('company_name'),
            company_address=validated_data.get('company_address'),
            gstin=validated_data.get('gstin'),
            language=validated_data.get('language')
        )
        return user






from .models import Product, Category

class ProductSerializer(serializers.ModelSerializer):
    seller = serializers.CharField(source="seller.username", read_only=True)  
    category_name = serializers.CharField(source="category.name", read_only=True) 
    class Meta:
        model = Product
        fields = '__all__' 
        read_only_fields = ['seller']



class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class WishlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = ['id', 'product']

class CartProductSerializer(serializers.ModelSerializer):
    total_price = serializers.SerializerMethodField()
    product_name = serializers.SerializerMethodField()
    product_image = serializers.SerializerMethodField()

    class Meta:
        model = CartProduct
        fields = ['id', 'product', 'quantity', 'total_price', 'product_name', 'product_image']

    def get_total_price(self, obj):
        return obj.total_price()

    def get_product_name(self, obj):
        return obj.product.title if obj.product else None  # Assuming Product model has 'name' field

    def get_product_image(self, obj):
        return obj.product.image if obj.product and obj.product.image else None  # Assuming Product model has 'image' field


class CartSerializer(serializers.ModelSerializer):
    cart_products = CartProductSerializer(many=True, read_only=True)
    total_cart_value = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'cart_products', 'total_cart_value']

    def get_total_cart_value(self, obj):
        return sum(item.total_price() for item in obj.cart_products.all())

class OrderItemSerializer(serializers.ModelSerializer):
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'status','total_price']

    def get_total_price(self, obj):
        return obj.total_price()

class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'created_at', 'order_items']


class EnquirySerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.title", read_only=True)
    product_image = serializers.CharField(source="product.image", read_only=True)
    class Meta:
        model = Enquiry
        fields = ['id', 'product','product_name','product_image', 'quantity', 'status', 'created_at']

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['buyer'] = request.user
        return super().create(validated_data)
     
class EnquiryUpdateSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Enquiry
        fields = ['status']


class OrderItemStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['status']

    def validate_status(self, value):
        if self.instance.status != 'Pending' and value == "Cancelled" :
            raise serializers.ValidationError("Only pending orders can be cancelled.")
        if value not in [ "Pending", "Cancelled","Shipped","Out For Delivery","Delivered", "Completed"]:
            raise serializers.ValidationError("Invalid status update.")

        # Ensure status can only be updated if it's currently 'Pending'
    

        return value
