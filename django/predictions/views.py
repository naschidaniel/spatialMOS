"""The views of the predictions app"""

from django.shortcuts import render
from predictions.forms import addressForm, latlonForm
import requests

def addressprediction(request):
    """The function to display the spatialMOS predictions for a address."""
    
    context = {
        'address': addressForm(),
    }
    return render(request, 'predictions/addressprediction.html', context)

def predictions(request):
    """The function to display the spatialMOS plots."""

    spatialmosrun_req = requests.get('https://moses.tirol/api/spatialmosrun/last/tmp_2m/')
    if spatialmosrun_req.status_code == 200:
        spatialmosrun = spatialmosrun_req.json()
    else:
        spatialmosrun = None

    context = {
        'spatialmosrun': spatialmosrun,
    }
    return render(request, 'predictions/predictions.html', context)

def pointprediction(request):
    """The function to display the spatialMOS predictions for coordinates."""

    query_url = ""

    if request.method == 'GET':
        latlon = latlonForm(request.GET)

        if latlon.is_valid():
            latitude = latlon.cleaned_data['latitude']
            longitude = latlon.cleaned_data['longitude']

            query_string = f"lon={longitude}&lat={latitude}"

            # Photon software is open source and licensed under Apache License, Version 2.0
            # https://github.com/komoot/photon
            query_url = f"https://photon.komoot.de/reverse?{query_string}&limit=1"
    else:
        latlon = latlonForm()

    context = {
        'content': 'modelrun',
        'latlon': latlon,
        'query_url': query_url,
    }
    return render(request, 'predictions/pointprediction.html', context)
