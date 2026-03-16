from django.db import models

class Reaction(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    image = models.ForeignKey("ImageModel", on_delete=models.CASCADE)
    react = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'image')

    def __str__(self):
        return f'{self.user} to {self.image.id}: {"Like" if self.react else "Dislike"}'