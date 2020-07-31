from django.db import models

# Create your models here.
class SpatialmosRun(models.Model):
    available_parameter = (
        ("tmp_2m", "Temperatur 2m"),
        ("rh_2m", "Relative Luftfeuchte 2m"),
        ("wind_10m", "Windgeschwindigkeit 10m"),
    )
    anal_date = models.DateTimeField()
    parameter = models.CharField(max_length=10, default="tmp_2m", choices=available_parameter)
    complete = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.complete is False:
            return "{:30s} | {} | Not the entire model run is available.".format(self.get_parameter_display(), self.anal_date.strftime("%Y-%m-%d"))
        else:
            return "{:30s} | {} ".format(self.get_parameter_display(), self.anal_date.strftime("%Y-%m-%d"))

    class Meta:
        ordering = ['-anal_date', 'parameter']

class SpatialMosStep(models.Model):
    fig_nwp = models.ImageField(upload_to='')
    fig_nwp_sd = models.ImageField(upload_to='')
    fig_spatialmos = models.ImageField(upload_to='')
    fig_spatialmos_sd = models.ImageField(upload_to='')
    spatialmos_run = models.ForeignKey(SpatialmosRun, related_name="spatialmos_run", on_delete=models.CASCADE)
    valid_date = models.DateTimeField()
    step = models.IntegerField(default=-999)

    def __str__(self):
        return "{} | Valid: {} | Step: {}".format(self.spatialmos_run, self.valid_date.strftime("%Y-%m-%d %H:%M"), self.step)

    class Meta:
        ordering = ("spatialmos_run", "step")