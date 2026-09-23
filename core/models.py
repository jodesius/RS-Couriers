from django.db import models


class CloudinaryTestUpload(models.Model):
    """
    Temporary model used only to confirm Cloudinary is wired up correctly.
    Delete this once a real image-owning model (e.g. a gallery item) exists.
    """
    image = models.ImageField(upload_to='test_uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Test upload #{self.pk}'
