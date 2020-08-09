from django.shortcuts import render
import requests

# Create your views here.
def predictions(request):
    """The function to display the spatialMOS predictions."""
    spatialmos_run_req = requests.get('https://moses.tirol/api/spatialmosstep/last/tmp_2m/')
    spatialmos_run = spatialmos_run_req.json()

    context = {
        'content': spatialmos_run,
    }
    return render(request, 'predictions/predictions.html', context)

def pointpredictions(request):
    """The function to display the spatialMOS predictions."""
    context = {
        'content': 'modelrun',
    }
    return render(request, 'predictions/pointpredictions.html', context)