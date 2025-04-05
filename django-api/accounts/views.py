from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from accounts.serializers import (
    UserSerializer, UserLoginSerializer, PasswordChangeSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer,
    UserProfileUpdateSerializer, EmailAuthTokenSerializer
)
from accounts.permissions import IsAdminUser


User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing users.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        """
        - Allow anyone to register
        - Only admin can list all users
        - Users can view and update their own profile
        """
        if self.action == 'create':
            permission_classes = [permissions.AllowAny]
        elif self.action in ['list']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Regular users can only see their own data.
        Admins can see all users.
        """
        user = self.request.user
        if user.is_staff:
            return User.objects.all()
        return User.objects.filter(id=user.id)

    @action(
        detail=False,
        methods=['post'],
        url_path='login',
        url_name='login',
        authentication_classes=[],
        permission_classes=[permissions.AllowAny]
    )
    def login(self, request):
        """
        API endpoint for user login.
        """
        print(f'Request data in login attempt {request.data}')
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {'detail': 'Invalid email or password.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        print(f"The password check value is {user.check_password(password)}")
        if not user.check_password(password):
            return Response(
                {'detail': 'Invalid email or password.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Generate or get auth token
        token, created = Token.objects.get_or_create(user=user)

        # Get user data
        user_serializer = UserSerializer(user)

        return Response({
            'token': token.key,
            'user': user_serializer.data
        })

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def logout(self, request):
        """
        API endpoint for user logout.
        """
        # Delete the user's token
        try:
            request.user.auth_token.delete()
        except Exception:
            pass

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def change_password(self, request):
        """
        API endpoint for changing password.
        """
        serializer = PasswordChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['new_password']

        # Check old password
        if not user.check_password(old_password):
            return Response(
                {'old_password': 'Wrong password.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Set new password
        user.set_password(new_password)
        user.save()

        # Update token
        Token.objects.filter(user=user).delete()
        token = Token.objects.create(user=user)

        return Response({
            'detail': 'Password updated successfully.',
            'token': token.key
        })

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def reset_password_request(self, request):
        """
        API endpoint for requesting a password reset.
        """
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email=email)

            # Generate reset token
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            # Create password reset link
            reset_link = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}"

            # Send email
            send_mail(
                'Password Reset Request',
                f'Please click the following link to reset your password: {reset_link}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )

        except User.DoesNotExist:
            # We don't want to reveal whether an email exists
            pass

        return Response({
            'detail': 'Password reset email has been sent if the email exists in our system.'
        })

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def reset_password_confirm(self, request):
        """
        API endpoint for confirming a password reset.
        """
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uid = serializer.validated_data['uid']
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']

        try:
            # Decode user id
            uid = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid)

            # Check token validity
            if not default_token_generator.check_token(user, token):
                return Response(
                    {'detail': 'Invalid reset link or it has expired.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Set new password
            user.set_password(new_password)
            user.save()

            return Response({
                'detail': 'Password has been reset successfully.'
            })

        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response(
                {'detail': 'Invalid reset link or it has expired.'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """
        API endpoint for getting the current user's profile.
        """
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['put', 'patch'], permission_classes=[permissions.IsAuthenticated])
    def update_profile(self, request):
        """
        API endpoint for updating the current user's profile.
        """
        serializer = UserProfileUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Return the full user data
        return Response(UserSerializer(request.user).data)


class CustomObtainAuthToken(ObtainAuthToken):
    """
    Custom token auth view that returns user data along with token.
    """
    serializer_class = EmailAuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)

        return Response({
            'token': token.key,
            'user': UserSerializer(user).data
        })


