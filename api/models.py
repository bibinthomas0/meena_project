from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class CustomUser(AbstractUser):
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    password = models.CharField(max_length=255)
    is_seller = models.BooleanField(default=False)
    is_buyer = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)
    pincode = models.CharField(max_length=6, default="000000")
    district = models.CharField(max_length=255, default="Unknown District")
    location = models.CharField(max_length=255)
    date_of_birth = models.DateField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    #if seller selected is_seller = True and fill the below fields
    company_name = models.CharField(max_length=255, null=True, blank=True)
    company_address = models.CharField(max_length=255, null=True, blank=True)
    gstin = models.CharField(max_length=15, null=True, blank=True)
    selected_pincodes = models.TextField(null=True, blank=True)  # Store as a comma-separated string
    def __str__(self):
        return self.username





class Product(models.Model):
    seller = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='products'
    )

    category = models.ForeignKey("Category", on_delete=models.CASCADE, related_name="products")
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    image = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

  
class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)


    def __str__(self):
        return self.name

class Wishlist(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="wishlist")
    product = models.ForeignKey("Product", on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'product')

class Cart(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="cart")
    created_at = models.DateTimeField(auto_now_add=True)

class CartProduct(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cart_products")
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
        return self.product.price * self.quantity

class Order(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="orders")
    created_at = models.DateTimeField(auto_now_add=True)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_items")
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    status = models.CharField(max_length=20,  default="Pending")

    def total_price(self):
        return self.product.price * self.quantity

class Enquiry(models.Model):
    buyer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="enquiries")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="enquiries")
    quantity = models.PositiveIntegerField()
    status = models.CharField(
        max_length=20,
        choices=[("Pending", "Pending"), ("Accepted", "Accepted"), ("Rejected", "Rejected")],
        default="Pending"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.buyer.user.username} - {self.product.title} ({self.status})"


class HelpAndSupport(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="help_comments")
    comment = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    reply_comment = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Comment by {self.user.username}"