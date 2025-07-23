import os.path
import uuid

from django.core.files.storage import FileSystemStorage


class MealStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=100):
        extension = os.path.splitext(name)[1]
        new_name = f"custom_{uuid.uuid4().hex}{extension}"
        return super().get_available_name(new_name,max_length)
