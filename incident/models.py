from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import random
from django.core.exceptions import ValidationError

# This is the Profile model that will save the user Profile.
class Profile(models.Model):
    USER_TYPE_CHOICES = [
        ('Individual', 'Individual'),
        ('Enterprises', 'Enterprises'),
        ('Government', 'Government'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=15, choices=USER_TYPE_CHOICES)
    address = models.TextField()
    country = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    isd_code = models.CharField(max_length=5)
    mobile_number = models.CharField(max_length=15)
    fax = models.CharField(max_length=15, blank=True, null=True)
    # phone = models.CharField(max_length=15, blank=True, null=True)
    
    def clean(self):
        self.validate_phone_number(self.phone)

    def __str__(self):
        return f"{self.user.username} - {self.user_type}"
    
            
# This is the Incident model that will save the Incident details
class Incident(models.Model):
    ORGANIZATION_CHOICES = [
        ('Enterprise', 'Enterprise'),
        ('Government', 'Government'),
    ]

    PRIORITY_CHOICES = [
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low')
    ]

    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('In progress', 'In progress'),
        ('Closed', 'Closed')
    ]
    organization_type = models.CharField(max_length=15, choices=ORGANIZATION_CHOICES)
    incident_id = models.CharField(max_length=15, unique=True, blank=True)
    reporter = models.ForeignKey(User, on_delete=models.CASCADE)
    incident_details = models.TextField()
    reported_at = models.DateTimeField(default=timezone.now)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Open')


    # To automatically save the incident_id during the creation of a new entry in the database.
    def save(self, *args, **kwargs):
        if not self.incident_id:
            self.incident_id = self.generate_incident_id()
        super().save(*args, **kwargs)

    # To generate the unique [inciddent_id]
    def generate_incident_id(self):
        current_year = timezone.now().year
        random_number = random.randint(10000, 99999)
        incident_id = f'RMG{random_number}{current_year}'
        while Incident.objects.filter(incident_id=incident_id).exists():
            random_number = random.randint(10000, 99999)
            incident_id = f'RMG{random_number}{current_year}'
        return incident_id

    def __str__(self):
        return f"Incident {self.incident_id} reported by {self.reporter}"





from django.db import models

class Publisher(models.Model):
    name = models.CharField(max_length=100)
    established_year = models.IntegerField()

    def __str__(self):
        return self.name

class Author(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    birthdate = models.DateField()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Book(models.Model):
    title = models.CharField(max_length=200)
    publication_date = models.DateField()
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)
    authors = models.ManyToManyField(Author)

    def __str__(self):
        return self.title












from django.db import models

class Department(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Employee(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='employees')

    def __str__(self):
        return self.name
