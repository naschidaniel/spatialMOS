"""The views of the predictions app"""

from django.shortcuts import render
from predictions.forms import addressForm, latlonForm
import requests


# Helper functions
def request_url(request_url):
    """A function which handles requests to an API interface."""
    error = ""
    data = None
    try:
        data_req = requests.get(request_url)
        if data_req.status_code == 200:
            data = data_req.json()
        else:
            error = f"Die API Schnittstelle '{request_url}' gab den Status {data_req.status_code} zurück."
        return data, error
    except:
        error = f"Die API Schnittstelle '{request_url}' konnte nicht abgefragt werden."
        return data, error

def photon_data(photon_url, query_string):
    """A Function to precess the API Call to photon.komoto.de"""

    # Photon software is open source and licensed under Apache License, Version 2.0
    # https://github.com/komoot/photon
    photon_json, error = request_url(photon_url)

    spatialmos_api_url = ""
    photon_properties = ""

    if error == "":
        try:
            photon_properties = photon_json['features'][0]['properties']
            if photon_properties['state'] in ['Tyrol', 'Trentino-Alto Adige/Südtirol']:
                photon_coordinates = photon_json['features'][0]['geometry']['coordinates']
                spatialmos_api_url = f"/api/spatialmospoint/last/tmp_2m/{photon_coordinates[1]}/{photon_coordinates[0]}/"
            else:
                error = f"Ihre Eingabe '{query_string}' führte zu einem Ergebnis außerhalb von Nord- und Südtirols."
        except:
            error = f"Ihre Suchanfrage '{query_string}' führte zu keinem brauchbaren Ergebnis."
    return photon_properties, spatialmos_api_url, error

# Views
def addressprediction(request):
    """The function to display the spatialMOS predictions for a address."""
    photon_url = ""
    photon_properties = dict()
    spatialmos_api_url = ""
    error = ''
    
    if request.method == 'GET':
        address_form = addressForm(request.GET)

        if address_form.is_valid():
            country = address_form.cleaned_data['country']
            postcode = str(address_form.cleaned_data['postcode'])
            city = address_form.cleaned_data['city']
            street = address_form.cleaned_data['street']
            housenumber = str(address_form.cleaned_data['housenumber'])

            if country == "Italy":
                state = "Trentino-Alto Adige/Südtirol"
            else:
                state = "Tyrol"

            query_list = [city, street, housenumber, postcode, state, country]
            
            query_list_filtered = []
            for value in query_list:
                if value not in ['', 'None']:
                    query_list_filtered.append(value)
            
            query_string = ','.join(query_list_filtered)
            
            photon_url = f"http://photon.komoot.de/api/?q=?{query_string}&limit=1"
            photon_properties, spatialmos_api_url, error = photon_data(photon_url, query_string)
    else:
        address_form = addressForm()

    context = {
        'address_form': address_form,
        'photon_properties': photon_properties,
        'query_url': photon_url,
        'spatialmos_api_url': spatialmos_api_url,
        'error': error
    }
    
    return render(request, 'predictions/addressprediction.html', context)


def pointprediction(request):
    """The function to display the spatialMOS predictions for coordinates."""

    photon_url = ""
    photon_properties = dict()
    spatialmos_api_url = ""
    error = ''

    if request.method == 'GET':
        latlon_form = latlonForm(request.GET)

        if latlon_form.is_valid():
            latitude = latlon_form.cleaned_data['latitude']
            longitude = latlon_form.cleaned_data['longitude']

            query_string = f"lon={longitude}&lat={latitude}"

            photon_url = f"http://photon.komoot.de/reverse?{query_string}&limit=1"
            photon_properties, spatialmos_api_url, error = photon_data(photon_url, query_string)
    else:
        latlon_form = latlonForm()

    context = {
        'latlon_form': latlon_form,
        'photon_properties': photon_properties,
        'query_url': photon_url,
        'spatialmos_api_url': spatialmos_api_url,
        'error': error
        }

    return render(request, 'predictions/pointprediction.html', context)


def predictions(request):
    """The function to display the spatialMOS plots."""
    spatialmosrun, error = request_url('https://moses.tirol/api/spatialmosrun/last/tmp_2m/')

    context = {
        'spatialmosrun': spatialmosrun,
        'error': error
    }
    return render(request, 'predictions/predictions.html', context)