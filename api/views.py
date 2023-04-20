from django.shortcuts import render
from django.core.mail import send_mail
from django.http import JsonResponse, HttpResponse
import random
import string
import datetime


from .serializers import *
from .models import *
from .authentication import (
    create_access_token, 
    JWTAuthentication, 
    decode_refresh_token
)    

from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework import exceptions, status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.settings import api_settings
from rest_framework import (
    viewsets,
    generics,
    authentication,
    permissions
)


error404 = 404
error500 = 500
error400 = 400
message404 = "Request not found!"
message500 = "Internal Server Error!"
message400 = "Bad Request!"

# Create your views here.
class RoleView(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer


class UserView(viewsets.ModelViewSet):  
    queryset = User.objects.all().order_by('-created_at')
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user"""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class CustomUserView(APIView):

    @api_view(['POST'])
    def register_user(request):
        data = request.data

        if data['password'] != data['password_confirm']:
            raise exceptions.APIException('Passwords do not match!')

        serializer = UserSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


    @api_view(['POST'])
    def login(request):
        email = request.data['email']
        password = request.data['password']

        user = User.objects.filter(email=email).first()

        if user is None:
            raise exceptions.AuthenticationFailed('Invalid credentials')

        if not user.check_password(password):
            raise exceptions.AuthenticationFailed('Invalid credentials')

        access_token = create_access_token(user.id)
        # refresh_token = create_refresh_token(user.id)

        UserToken.objects.create(
            user_id=user.id,
            # token=refresh_token,
            expired_at=datetime.datetime.utcnow() + datetime.timedelta(days=7)
        )

        response = Response()
        # response.set_cookie(key='refresh_token', value=refresh_token, httponly=True)
        response.data = {
            'access_token': access_token,
            # 'refresh_token' : refresh_token
        }
        return response


    @api_view(['GET'])
    @authentication_classes([JWTAuthentication])
    def current_user(request):
        return Response(UserSerializer(request.user).data)


    @api_view(['GET'])
    def user_profile(request):
        email = request.GET.get('email', 'default')

        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            return JsonResponse({"detail": message404}, status=error404)

        res = User.objects.filter(email=email).values('id', 'first_name', 'last_name', 'password', 'email', 'role__name', 'role', 'is_active')
                                                            
        result = list(res)
        return Response(result)


    @api_view(['PATCH'])
    @authentication_classes([JWTAuthentication])
    def update_profile(request, *args, **kwargs):
    
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


    @api_view(['POST'])
    def refresh_token(request):
        # refresh_token = request.COOKIES.get('refresh_token')
        refresh_token = request.COOKIES.get('refresh_token')
        id = decode_refresh_token(refresh_token)

        if not UserToken.objects.filter(
                user_id=id,
                token=refresh_token,
                expired_at__gt=datetime.datetime.now(tz=datetime.timezone.utc)
        ).exists():
            raise exceptions.AuthenticationFailed('unauthenticated')

        access_token = create_access_token(id)

        return Response({
            'refresh_token': access_token
        })


    @api_view(['POST'])
    def logout(request):
        refresh_token = request.COOKIES.get('refresh_token')
        UserToken.objects.filter(token=refresh_token).delete()

        response = Response()
        response.delete_cookie(key='refresh_token')
        response.data = {
            'message': 'success'
        }

        return response


    @api_view(['POST'])
    def forgot_password(request):
        email = request.data['email']
        token = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))

        Reset.objects.create(
            email=email,
            token=token
        )

        url = 'http://localhost:3000/reset-password/' + token

        send_mail(
            subject='Reset your password!',
            message='Click <a href="%s">here</a> to reset your password!' % url,
            from_email='sales_inventory@gmail.com',
            recipient_list=[email],
            fail_silently=False
        )

        return Response({
            'message': 'success'
        })
   

    @api_view(['POST'])
    def reset_password(request):
        data = request.data

        if data['password'] != data['password_confirm']:
            raise exceptions.APIException('Passwords do not match!')

        reset_password = Reset.objects.filter(token=data['token']).first()

        if not reset_password:
            raise exceptions.APIException('Invalid link!')

        user = User.objects.filter(email=reset_password.email).first()

        if not user:
            raise exceptions.APIException('User not found!')

        user.set_password(data['password'])
        user.save()

        return Response({
            'message': 'success'
        })


class CustomerView(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


class CategoryView(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class SupplierView(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer


class ProductView(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('-created_at')
    serializer_class = ProductSerializer


class TransactionView(viewsets.ModelViewSet):
    queryset = Transaction.objects.all().order_by('-created_at')
    serializer_class = TransactionSerializer
 

class Transaction_ItemView(viewsets.ModelViewSet):
    queryset = Transaction_Item.objects.all()
    serializer_class = Transaction_ItemSerializer
  

class CustomView(APIView):

    @api_view(['GET'])
    def get_products_category_supplier(request):
       
        res = Product.objects.order_by('-created_at').values(
                        'id','product_code','name','category__name','supplier__company_name','qty_on_hand','price','description','date_stock_in','created_by','created_at','updated_at'
                    )
        data = list(res)
        return Response(data)

    @api_view(['GET'])
    def get_product_detail(request):
     
        product_id = request.GET.get('product_id', 'default')

        try:
            Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return JsonResponse({"detail": message404}, status=error404)
       
        res = Product.objects.order_by('-created_at').filter(id=product_id).values(
                        'id','product_code','name','category__name','supplier__company_name','qty_on_hand','price','description','date_stock_in','created_by__first_name','created_by__last_name','created_at','updated_at', 'image'
                    )
        result = list(res)
        return Response(result)   


    @api_view(['GET'])
    def get_users_role(request):
        res = User.objects.order_by('-created_at').filter(role=2).values(
               'id','first_name','last_name','email','role__name','created_at','updated_at', 'is_active')
        data = list(res)
        return Response(data)

    @api_view(['PATCH'])
    def update_users(request, pk):
        user_id = User.objects.get(pk=pk)

        serializer = UserSerializer(user_id, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @api_view(['GET'])
    def get_transaction_customer(request):

        res = Transaction.objects.order_by('-created_at').values('id','transaction_code','customer__first_name','customer__last_name','items_quantity','tax','total_price','created_at')
        result = list(res)
        return Response(result)

    @api_view(['GET'])
    def get_transaction_item_detail(request):
        transaction_id = request.GET.get('transaction_id', 'default')

        try:
            Transaction_Item.objects.get(id=transaction_id)
        except Transaction_Item.DoesNotExist:
            return JsonResponse({"detail": message404}, status=error404)
       
        res = Transaction_Item.objects.order_by('-id').filter(id=transaction_id).values('id','transaction__transaction_code','product__product_code','product__name','price','quantity')
        result = list(res)
        return Response(result)

    @api_view(['GET'])
    def get_current_user(request):
        user_id = request.GET.get('user_id', 'default')

        try:
            User.objects.get(id=user_id)
        except User.DoesNotExist:
            return JsonResponse({"detail": message404}, status=error404)

        res = User.objects.filter(id=user_id).values('id', 'first_name', 'last_name', 'email', 'role__name', 'is_active')
                                                            
        result = list(res)
        return Response(result)

    @api_view(['GET'])
    def count_customers(request):
        res = Customer.objects.all().count()
        return Response({'count': res})   

    @api_view(['GET'])
    def total_users(request):
        role = request.GET.get('role', 'default')
        count = len(set(User.objects.filter(role=role)))
        data = {"total_users": count}
        return Response(data)

    @api_view(['GET'])
    def count_products(request):
        res = Product.objects.all().count()
        return Response({'count': res})

    @api_view(['GET'])
    def count_suppliers(request):
        res = Supplier.objects.all().count()
        return Response({'count': res})

    @api_view(['GET'])
    def count_transactions(request):
        res = Transaction.objects.all().count()
        return Response({'count': res})