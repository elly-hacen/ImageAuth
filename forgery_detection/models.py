from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # Extending AbstractUser for username, email, etc.
    created_at = models.DateTimeField(auto_now_add=True, help_text="Account Creation Date")

    def __str__(self):
        return self.username

class Image(models.Model):
    filename = models.CharField(max_length=255, help_text="Filename")
    upload_time = models.DateTimeField(auto_now_add=True, help_text="Upload Timestamp")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='images', help_text="Uploaded By")
    status = models.CharField(max_length=50, help_text="Processing Status")

    def __str__(self):
        return self.filename

class Metadata(models.Model):
    tag = models.CharField(max_length=255, help_text="Metadata Tag")
    value = models.TextField(help_text="Metadata Value")
    image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name='metadata', help_text="Related Image")

    def __str__(self):
        return f"{self.tag}: {self.value}"

class AnalysisResult(models.Model):
    prediction = models.CharField(max_length=20, help_text="Fake or Authentic")
    confidence_score = models.FloatField(help_text="Confidence (0-1)")
    analyzed_at = models.DateTimeField(auto_now_add=True, help_text="Analysis Time")
    image = models.OneToOneField(Image, on_delete=models.CASCADE, related_name='analysis_result', help_text="Related Image")

    def __str__(self):
        return f"{self.prediction} ({self.confidence_score:.2f})"

class UploadLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='upload_logs', help_text="User")
    image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name='upload_logs', help_text="Image")
    timestamp = models.DateTimeField(auto_now_add=True, help_text="Upload Time")
    ip_address = models.GenericIPAddressField(help_text="Uploader IP")

    def __str__(self):
        return f"Upload by {self.user} at {self.timestamp}"
