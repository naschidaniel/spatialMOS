from django.db import models

# Create your models here.
class SpatialMosRun(models.Model):
    available_parameter = (
        ("tmp_2m", "Temperatur 2m"),
        ("rh_2m", "Relative Luftfeuchte 2m"),
        ("wind_10m", "Windgeschwindigkeit 10m"),
    )
    parameter = models.CharField(max_length=10, default="tmp_2m", choices=available_parameter)
    anal_date = models.DateTimeField()
    complete = models.BooleanField(default=False)

    def __str__(self):
        return_string = f"{self.get_parameter_display():30s} | {self.anal_date.strftime('%Y-%m-%d')}"
        if self.complete is False:
            return f"{return_string} | Not all steps were imported successfully."
        else:
            return return_string

    class Meta:
        ordering = ['-anal_date', 'parameter']

class SpatialMosStep(models.Model):
    spatialmos_run = models.ForeignKey(SpatialMosRun, related_name="steps", on_delete=models.CASCADE)
    valid_date = models.DateTimeField()
    step = models.IntegerField(default=-999)
    filename_nwp_mean = models.ImageField(upload_to='')
    filename_nwp_spread = models.ImageField(upload_to='')
    filename_spatialmos_mean = models.ImageField(upload_to='')
    filename_spatialmos_spread = models.ImageField(upload_to='')

    def __str__(self):
        return "{} | Valid: {} | Step: {:03d}".format(self.spatialmos_run, self.valid_date.strftime("%Y-%m-%d %H:%M"), self.step)

    class Meta:
        ordering = ("spatialmos_run", "step")


class SpatialMosPoint(models.Model):
    spatialmos_step = models.ForeignKey(SpatialMosStep, related_name="points", on_delete=models.CASCADE)
    lat = models.DecimalField(max_digits=16, decimal_places=14, default=None)
    lon = models.DecimalField(max_digits=16, decimal_places=14, default=None)
    samos_mean = models.DecimalField(max_digits=6, decimal_places=2, default=None)
    samos_spread = models.DecimalField(max_digits=6, decimal_places=2, default=None)

    def __str__(self):
        return f"{self.spatialmos_step} | Location: {self.lat}, {self.lon} | mean: {self.samos_mean} spread: {self.samos_spread}"

    class Meta:
        ordering = ("spatialmos_step", "-lat", "lon")
        indexes = [
            models.Index(fields=['spatialmos_step', 'lat', 'lon'])
        ]
