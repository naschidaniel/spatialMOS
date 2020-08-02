from django.db import models

# Create your models here.
class SpatialMosRun(models.Model):
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
            return "{:30s} | {} | Not all steps were imported successfully..".format(self.get_parameter_display(), self.anal_date.strftime("%Y-%m-%d"))
        else:
            return "{:30s} | {} ".format(self.get_parameter_display(), self.anal_date.strftime("%Y-%m-%d"))

    class Meta:
        ordering = ['-anal_date', 'parameter']

class SpatialMosStep(models.Model):
    filename_nwp_mean = models.ImageField(upload_to='')
    filename_nwp_spread = models.ImageField(upload_to='')
    filename_spatialmos_mean = models.ImageField(upload_to='')
    filename_spatialmos_spread = models.ImageField(upload_to='')
    spatialmos_run = models.ForeignKey(SpatialMosRun, related_name="spatialmos_run", on_delete=models.CASCADE)
    valid_date = models.DateTimeField()
    step = models.IntegerField(default=-999)

    def __str__(self):
        return "{} | Valid: {} | Step: {}".format(self.spatialmos_run, self.valid_date.strftime("%Y-%m-%d %H:%M"), self.step)

    class Meta:
        ordering = ("spatialmos_run", "step")

class SpatialMosPoint(models.Model):
    lat = models.DecimalField(max_digits=16, decimal_places=14, default=None)
    lon = models.DecimalField(max_digits=16, decimal_places=14, default=None)
    samos_mean = models.DecimalField(max_digits=6, decimal_places=2, default=None)
    samos_spread = models.DecimalField(max_digits=6, decimal_places=2, default=None)
    spatialmos_step = models.ForeignKey(SpatialMosStep, related_name="spatialmos_step", on_delete=models.CASCADE)

    def __str__(self):
        return "{} | Location: {}, {} | mean: {} spread: {}".format(self.spatialmos_step, self.lat, self.lon, self.samos_mean, self.samos_spread)

    class Meta:
        ordering = ("spatialmos_step", "-lat", "lon")
        indexes = [
            models.Index(fields=['spatialmos_step', 'lat', 'lon'])
        ]
