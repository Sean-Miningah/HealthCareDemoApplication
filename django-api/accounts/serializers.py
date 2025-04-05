from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model
from django.db import transaction
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
    """
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    password_confirmation = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'phone_number',
                  'role', 'password', 'password_confirmation', 'created_at']
        read_only_fields = ['id', 'created_at']
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate(self, data):
        # Check that the two password entries match
        if data.get('password') != data.get('password_confirmation'):
            raise serializers.ValidationError({"password_confirmation": "Passwords must match."})

        # Validate password complexity
        # validate_password(data.get('password'))
        return data

    def create(self, validated_data):
        # Remove password confirmation from the data
        validated_data.pop('password_confirmation', None)

        with transaction.atomic():
            # Create the user
            user = User.objects.create_user(
                email=validated_data.pop('email'),
                password=validated_data.pop('password'),
                **validated_data
            )

        return user

class EmailAuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField(label=_("Email"))
    password = serializers.CharField(
        label=_("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'),
                                email=email, password=password)

            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "email" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    """
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'})


class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(style={'input_type': 'password'})
    new_password = serializers.CharField(style={'input_type': 'password'})
    new_password_confirmation = serializers.CharField(style={'input_type': 'password'})

    def validate(self, data):
        # Check that the two new password entries match
        if data.get('new_password') != data.get('new_password_confirmation'):
            raise serializers.ValidationError({"new_password_confirmation": "New passwords must match."})

        # Validate new password complexity
        # validate_password(data.get('new_password'))
        return data


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer for requesting a password reset.
    """
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer for confirming a password reset.
    """
    token = serializers.CharField()
    uid = serializers.CharField()
    new_password = serializers.CharField(style={'input_type': 'password'})
    new_password_confirmation = serializers.CharField(style={'input_type': 'password'})

    def validate(self, data):
        # Check that the two new password entries match
        if data.get('new_password') != data.get('new_password_confirmation'):
            raise serializers.ValidationError({"new_password_confirmation": "New passwords must match."})

        # Validate new password complexity
        validate_password(data.get('new_password'))
        return data


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating a user's profile.
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number']