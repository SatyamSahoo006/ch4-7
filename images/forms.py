from django import forms
from .models import Image


class ImageCreateForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['title', 'url', 'description']
        widgets = {
            'url': forms.HiddenInput,
        }

    def clean_url(self):
        url = self.cleaned_data['url']
        valid_extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp']
        extension = url.rsplit('.', 1)[-1].lower()
        if extension not in valid_extensions:
            raise forms.ValidationError('The given URL does not match valid image extensions.')
        return url

    def save(self, force_insert=False, force_update=False, commit=True):
        image = super().save(commit=False)
        image_url = self.cleaned_data['url']
        name = f'{image.slug}.{image_url.rsplit(".", 1)[-1].lower()}'
        image.image.save(name, self._download_image(image_url), save=False)
        if commit:
            image.save()
        return image

    def _download_image(self, url):
        import urllib.request
        from django.core.files.base import ContentFile
        response = urllib.request.urlopen(url)
        return ContentFile(response.read())
