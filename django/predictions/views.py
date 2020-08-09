from django.shortcuts import render
import requests

# Create your views here.
def predictions(request):
    """The function to display the spatialMOS predictions."""
    spatialmosrun_req = requests.get('https://moses.tirol/api/spatialmosrun/last/tmp_2m/')
    
    if spatialmosrun_req.status_code == 200:
        spatialmosrun = spatialmosrun_req.json()
    else:
        spatialmosrun = None

    context = {
        'spatialmosrun': spatialmosrun,
    }
    return render(request, 'predictions/predictions.html', context)

def pointpredictions(request):
    """The function to display the spatialMOS predictions."""
    context = {
        'content': 'modelrun',
    }
    return render(request, 'predictions/pointpredictions.html', context)