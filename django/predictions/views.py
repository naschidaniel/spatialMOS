"""The views of the predictions app"""

from django.shortcuts import render
from predictions.forms import addressForm, latlonForm
import requests


# Helper functions
def request_url(request_url):
    """A function which handles requests to an API interface."""
    data_req = requests.get(request_url)
    if data_req.status_code == 200:
        data = data_req.json()
    else:
        data = None
    return data


# Views
def addressprediction(request):
    """The function to display the spatialMOS predictions for a address."""
    photon_url = ""
    photon_properties = dict()
    spatialmos_api_url = ""
    photon_json = ""

    
    if request.method == 'GET':
        address_form = addressForm(request.GET)

        if address_form.is_valid():
            country = address_form.cleaned_data['country']
            city = address_form.cleaned_data['city']
            street = address_form.cleaned_data['street']
            housenumber = str(address_form.cleaned_data['housenumber'])
            postcode = str(address_form.cleaned_data['postcode'])

            query_list = [country, postcode, city, street, housenumber]
            query_string = ','.join(query_list)
            
            # Photon software is open source and licensed under Apache License, Version 2.0
            # https://github.com/komoot/photon
            photon_url = f"https://photon.komoot.de/api/?q=?{query_string}&limit=1"
            photon_json = request_url(photon_url)


    else:
        address_form = addressForm()

    context = {
        'address_form': address_form,
        'photon_properties': photon_json,
        'query_url': photon_url,
        'spatialmos_api_url': spatialmos_api_url
    }
    
    return render(request, 'predictions/addressprediction.html', context)


def pointprediction(request):
    """The function to display the spatialMOS predictions for coordinates."""

    photon_url = ""
    photon_properties = dict()
    spatialmos_api_url = ""

    if request.method == 'GET':
        latlon_form = latlonForm(request.GET)

        if latlon_form.is_valid():
            latitude = latlon_form.cleaned_data['latitude']
            longitude = latlon_form.cleaned_data['longitude']

            query_string = f"lon={longitude}&lat={latitude}"

            # Photon software is open source and licensed under Apache License, Version 2.0
            # https://github.com/komoot/photon
            photon_url = f"https://photon.komoot.de/reverse?{query_string}&limit=1"
            photon_json = request_url(photon_url)

            photon_properties = photon_json['features'][0]['properties']
            photon_coordinates = photon_json['features'][0]['geometry']['coordinates']
            spatialmos_api_url = f"http://localhost/api/spatialmospoint/last/tmp_2m/{photon_coordinates[1]}/{photon_coordinates[0]}/"

    else:
        latlon_form = latlonForm()

    context = {
        'latlon_form': latlon_form,
        'photon_properties': photon_properties,
        'query_url': photon_url,
        'spatialmos_api_url': spatialmos_api_url
        }

    return render(request, 'predictions/pointprediction.html', context)


def predictions(request):
    """The function to display the spatialMOS plots."""
    spatialmosrun = request_url('https://moses.tirol/api/spatialmosrun/last/tmp_2m/')

    context = {
        'spatialmosrun': spatialmosrun,
    }
    return render(request, 'predictions/predictions.html', context)