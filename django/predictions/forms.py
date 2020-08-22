"""The forms for spatialMOS"""

from django import forms


class addressForm(forms.Form):
    """The form for address inputs"""
    COUNTRY_CHOICES = (('AT', 'Österreich'), ('IT', 'Italien'))

    street = forms.CharField(label='Straße', required=False)
    number = forms.IntegerField(label='Hausnummer', required=False)
    zipcode = forms.IntegerField(label='PLZ', required=False)
    city = forms.CharField(label='Ort', required=True)
    country = forms.ChoiceField(choices=COUNTRY_CHOICES, required=False)


class latlonForm(forms.Form):
    """The form for coordinates inputs"""
    latitude = forms.FloatField(label='Latitude', required=True, min_value=46, max_value=48)
    longitude = forms.FloatField(label='Longitude', required=True, min_value=9, max_value=12)
