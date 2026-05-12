from django.conf import settings
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_of_birth = models.DateField(blank=True, null=True)
    photo = models.ImageField(upload_to='users/%Y/%m/%d/', blank=True)
    following = models.ManyToManyField(
        'self',
        through='Contact',
        related_name='followers',
        symmetrical=False,
        blank=True,
    )

    def __str__(self):
        return f'Profile of {self.user.username}'


class Contact(models.Model):
    user_from = models.ForeignKey(
        Profile, related_name='rel_from_set', on_delete=models.CASCADE
    )
    user_to = models.ForeignKey(
        Profile, related_name='rel_to_set', on_delete=models.CASCADE
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']
        indexes = [models.Index(fields=['-created'])]

    def __str__(self):
        return f'{self.user_from} follows {self.user_to}'
