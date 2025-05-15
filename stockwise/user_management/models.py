from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    USER_TYPE_CHOICES = (
        ('manager', 'Project Manager'),
        ('warehouse', 'Warehouse Staff'),
        ('procurement', 'Procurement Officer'),
        ('supplier', 'Supplier'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    image = models.ImageField(upload_to='profile_pics/', default='default.jpg', blank=True)

    def get_user_type_display(self):
        return dict(self.USER_TYPE_CHOICES).get(self.user_type, self.user_type)

    def __str__(self):
        return f"{self.user.username} - {self.get_user_type_display()}"