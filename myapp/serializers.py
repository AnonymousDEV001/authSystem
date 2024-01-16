from rest_framework import serializers
from django.contrib.auth.models import Group
from .models import CustomUser


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('name',)


class CustomUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(max_length=150, required=True)
    last_name = serializers.CharField(max_length=150, required=True)
    password = serializers.CharField(min_length=8, write_only=True)
    # New field for password confirmation
    password2 = serializers.CharField(min_length=8, write_only=True)
    groups = GroupSerializer(many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'first_name', 'last_name', 'password',
                  'password2', 'last_login', 'date_joined', 'groups', 'provider')
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        if data.get('password') != data.get('password2'):
            raise serializers.ValidationError("Passwords do not match")
        return data

    def update(self, instance, validated_data):
        # Update fields other than the password directly
        instance.email = validated_data.get('email', instance.email)
        instance.first_name = validated_data.get(
            'first_name', instance.first_name)
        instance.last_name = validated_data.get(
            'last_name', instance.last_name)
        instance.is_verified = validated_data.get(
            'is_verified', instance.is_verified)

        password = validated_data.get('password')
        if password:
            instance.set_password(password)  # Hash the new password
        instance.save()
        return instance

    def create(self, validated_data):
        # Remove password2 from the validated data
        validated_data.pop('password2')
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance
