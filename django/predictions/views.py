from django.shortcuts import render

# Create your views here.
def predictions(request):
    """The function to display the spatialMOS predictions."""
    context = {
        'content': 'modelrun',
    }
    return render(request, 'predictions/predictions.html', context)

def pointpredictions(request):
    """The function to display the spatialMOS predictions."""
    context = {
        'content': 'modelrun',
    }
    return render(request, 'predictions/pointpredictions.html', context)