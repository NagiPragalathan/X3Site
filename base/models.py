from django.db import models
import uuid

class MyModel(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    code = models.TextField()
    explain = models.TextField()

    def __str__(self):
        return str(self.uuid)
