from django.core.validators import RegexValidator
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import Profile, Incident
import phonenumbers

# Custom validator for password
password_regex_validator = RegexValidator(
    regex=r'^(?=.*[A-Z])(?=.*\d)(?=.*[*#$])[A-Za-z\d@$!%*#?&]{8,}$',
    message="Password must be at least 8 characters long, contain at least one uppercase letter, one special character, and one digit."
)

def validate_phone_number(potential_number: str, country_code: str) -> bool:
    try:
        # If the country code starts with '+', remove it for phonenumbers.parse
        if country_code.startswith('+'):
            country_code = country_code[1:]
        
        # Parse the phone number using the country code
        phone_number_obj = phonenumbers.parse(potential_number, country_code)
    except phonenumbers.phonenumberutil.NumberParseException as e:
        return False

    # Check if the parsed number is valid
    if not phonenumbers.is_valid_number(phone_number_obj):
        return False

    return True

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['user_type', 'address', 'country', 'state', 'city', 'pincode',
                  'mobile_number', 'fax', 'isd_code']

class RegistrationSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()  # Nested serializer for the Profile model
    password = serializers.CharField(write_only=True, required=True, validators=[password_regex_validator])
    confirm_password = serializers.CharField(write_only=True, required=True)
    first_name = serializers.CharField(required=True, allow_blank=False)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password', 'confirm_password', 'profile']

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        if not attrs['first_name']:
            raise serializers.ValidationError({"first_name": "This field is required."})
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({"email": "A user with this email already exists."})
        
        # Validate phone number using ISD code
        mobile_number = attrs['profile']['mobile_number']
        isd_code = attrs['profile']['isd_code']
        if not validate_phone_number(mobile_number, isd_code):
            raise serializers.ValidationError({"mobile_number": "Invalid mobile number."})

        return attrs

    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        user = User(
            username=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
        )
        user.set_password(validated_data['password'])
        user.save()

        Profile.objects.create(
            user=user,
            user_type=profile_data['user_type'],
            address=profile_data['address'],
            country=profile_data['country'],
            state=profile_data['state'],
            city=profile_data['city'],
            pincode=profile_data['pincode'],
            mobile_number=profile_data['mobile_number'],
            fax=profile_data.get('fax')
        )
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

class IncidentSerializer(serializers.ModelSerializer):
    reporter = serializers.ReadOnlyField(source='reporter.username')

    class Meta:
        model = Incident
        fields = ['organization_type', 'incident_id', 'reporter', 'incident_details', 'priority', 'status', 'reported_at']
        read_only_fields = ['incident_id', 'reported_at', 'reporter']
        
    def create(self, validated_data):
        # Automatically set the reporter field to the currently authenticated user
        validated_data['reporter'] = self.context['request'].user
        return super().create(validated_data)

class ViewIncidentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Incident
        fields = "__all__"

class EditIncidentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Incident
        fields = ['incident_details', 'priority', 'status']

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("No user is associated with this email address.")
        return value

class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True, required=True, validators=[validate_password],  )
    confirm_password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data
