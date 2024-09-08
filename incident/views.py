from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from .models import Incident
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import default_token_generator
from rest_framework.permissions import IsAuthenticated
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.password_validation import validate_password
from django.urls import reverse
from .serializers import RegistrationSerializer, LoginSerializer, PasswordResetRequestSerializer, IncidentSerializer, ViewIncidentSerializer, EditIncidentSerializer, ForgotPasswordSerializer, ResetPasswordSerializer

# This API is for registering a new user
class RegisterAPIView(APIView):
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully", "status_code": 201}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# This API is for Login.
class LoginAPIView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            
            user = authenticate(request, username=email, password=password)
            if user is not None:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'message': 'Successfully logged in',
                    "status_code": 201,
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }, status=status.HTTP_200_OK)
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response({'error': 'Invalid input', 'details': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
# Api for create/update/View the Incident
class IncidentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None, *args, **kwargs):
        if pk:
            # Retrieve a specific incident
            try:
                incident = Incident.objects.get(pk=pk, reporter=request.user)
                serializer = ViewIncidentSerializer(incident)
                return Response({
                    'message': 'Successfully Fetched',
                    "status_code": 200,
                    "data" : serializer.data
                }, status=status.HTTP_200_OK)
                # return Response(serializer.data)
            except Incident.DoesNotExist:
                return Response({"error": "Incident not found or you do not have permission to view this incident."},
                                status=status.HTTP_404_NOT_FOUND)
        else:
            # Retrieve all incidents for the user
            incidents = Incident.objects.filter(reporter=request.user)
            serializer = ViewIncidentSerializer(incidents, many=True)
            return Response({
                    'message': 'Successfully Fetched',
                    "status_code": 200,
                    "data" : serializer.data
                }, status=status.HTTP_200_OK)
            # return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = IncidentSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(reporter=request.user)
            return Response({
                    'message': 'Successfully Created',
                    "status_code": 201,
                    "data" : serializer.data
                }, status=status.HTTP_201_CREATED)
            # return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None, *args, **kwargs):
        try:
            incident = Incident.objects.get(pk=pk, reporter=request.user)
        except Incident.DoesNotExist:
            return Response({"message": "Incident not found or you do not have permission to update this incident.", "status_code": 400},
                            status=status.HTTP_404_NOT_FOUND)

        serializer = EditIncidentSerializer(incident, data=request.data, partial=True)
        if serializer.is_valid():
            if incident.status == 'Closed':  # Assuming 'status' is a field on your model
                return Response({"message": "You cannot edit a closed incident.",  "status_code": 400 },
                                status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response({
                    'message': 'Successfully Updated',
                    # "status_code": 200,
                    "data" : serializer.data
                }, status=status.HTTP_201_CREATED)
            # return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Api for searched the Incident that has been created before.
class RetrieveIncidentByIdView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        incident_id = request.query_params.get('incident_id')
        if not incident_id:
            return Response({"error": "incident_id query parameter is required."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            incident = Incident.objects.get(incident_id=incident_id, reporter=request.user)
        except Incident.DoesNotExist:
            return Response({"error": "Incident not found or you do not have permission to view this incident."},
                            status=status.HTTP_404_NOT_FOUND)

        serializer = ViewIncidentSerializer(incident)
        return Response({
                    'message': 'Successfully item searched',
                    # "status_code": 200,
                    "data" : serializer.data
                }, status=status.HTTP_201_CREATED)
        # return Response(serializer.data)

# Api for forgot the password (this will send the link on the email)
class ForgotPasswordAPIView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_url = f"{request.scheme}://{request.get_host()}/reset-password/?uid={uid}&token={token}"
            send_mail(
                'Password Reset Request',
                reset_url,
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )
            return Response({"message": "Password reset email sent.", "status_code": 200}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# Api for set the new password ()
class ResetPasswordAPIView(APIView):
    def post(self, request):
        uid = request.query_params.get('uid')
        token = request.query_params.get('token')

        # Validate the new password and confirm password
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            new_password = serializer.validated_data['new_password']
            try:
                uid = urlsafe_base64_decode(uid).decode()
                user = User.objects.get(pk=uid)
            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                user = None

            # Check if the token is valid
            if user and default_token_generator.check_token(user, token):
                user.set_password(new_password)
                user.save()
                return Response({"message": "Password has been reset successfully.", "status_code": 200}, status=status.HTTP_200_OK)
            return Response({"error": "Invalid token or user ID."}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)