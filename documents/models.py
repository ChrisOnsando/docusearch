from django.db import models
from django.db.models import JSONField

class Document(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/')
    text_content = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploader_email = models.EmailField()
    embedding = JSONField(null=True, blank=True) 

    def __str__(self):
        return self.title
