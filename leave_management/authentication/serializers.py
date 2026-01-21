from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser, Role


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'is_verified', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'is_verified', 'created_at', 'updated_at']


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            raise serializers.ValidationError('Email and password are required')
        
        # Authenticate using Django's auth system
        user = authenticate(username=email, password=password)
        
        if user is None:
            raise serializers.ValidationError('Invalid email or password')
        
        if not user.is_active:
            raise serializers.ValidationError('User account is disabled')
        
        data['user'] = user
        return data


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'role'
        ]
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Passwords do not match'
            })
        
        if CustomUser.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({
                'email': 'A user with this email already exists'
            })
        
        if CustomUser.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError({
                'username': 'A user with this username already exists'
            })
        
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        # Set default role to EMPLOYEE if not specified
        if 'role' not in validated_data or not validated_data['role']:
            validated_data['role'] = Role.EMPLOYEE
        
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        
        return user


class GoogleOAuthSerializer(serializers.Serializer):
    id_token = serializers.CharField()
    access_token = serializers.CharField(required=False)
    
    def validate(self, data):
        if not data.get('id_token'):
            raise serializers.ValidationError('ID token is required')
        return data


class GitHubOAuthSerializer(serializers.Serializer):
    code = serializers.CharField()
    
    def validate(self, data):
        if not data.get('code'):
            raise serializers.ValidationError('Authorization code is required')
        return data


class TokenResponseSerializer(serializers.Serializer):
    access_token = serializers.CharField()
    refresh_token = serializers.CharField(required=False)
    token_type = serializers.CharField(default='Bearer')
    expires_in = serializers.IntegerField(required=False)
    user = UserSerializer()


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField(min_length=8)

    def validate(self, data):
        user = self.context.get('user')
        if not user:
            raise serializers.ValidationError('User context required')

        if not user.check_password(data['old_password']):
            raise serializers.ValidationError({
                'old_password': 'Current password is incorrect'
            })

        if data['old_password'] == data['new_password']:
            raise serializers.ValidationError({
                'new_password': 'New password must be different from current password'
            })

        return data

