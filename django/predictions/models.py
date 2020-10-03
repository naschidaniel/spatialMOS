"""The models for Predictions are listed here."""

from django.db import models



class SpatialMosRun(models.Model):
    """The model for a spatiaMOS run"""
    available_parameter = (
        ("tmp_2m", "Temperatur 2m"),
        ("rh_2m", "Relative Luftfeuchte 2m"),
        ("wind_10m", "Windgeschwindigkeit 10m"),
    )
    parameter = models.CharField(max_length=10, default="tmp_2m", choices=available_parameter)
    anal_date = models.DateTimeField()
    complete = models.BooleanField(default=False)

    def __str__(self):
        """Return Value in the Admin Panel"""
        return_string = f"{self.get_parameter_display():30s} | {self.anal_date.strftime('%Y-%m-%d')}"
        if self.complete is False:
            return f"{return_string} | Not all steps were imported successfully."
        else:
            return return_string

    class Meta:
        """Settings"""
        ordering = ['-anal_date', 'parameter']

class SpatialMosStep(models.Model):
    """The model for a spatiaMOS Step"""
    spatialmos_run = models.ForeignKey(SpatialMosRun, related_name="steps", on_delete=models.CASCADE)
    valid_date = models.DateTimeField()
    step = models.IntegerField(default=-999)
    filename_nwp_mean_sm = models.ImageField(upload_to='', default='')
    filename_nwp_mean_md = models.ImageField(upload_to='', default='')
    filename_nwp_mean_lg = models.ImageField(upload_to='', default='')
    filename_nwp_spread_sm = models.ImageField(upload_to='', default='')
    filename_nwp_spread_md = models.ImageField(upload_to='', default='')
    filename_nwp_spread_lg = models.ImageField(upload_to='', default='')
    filename_spatialmos_mean_sm = models.ImageField(upload_to='', default='')
    filename_spatialmos_mean_md = models.ImageField(upload_to='', default='')
    filename_spatialmos_mean_lg = models.ImageField(upload_to='', default='')
    filename_spatialmos_spread_sm = models.ImageField(upload_to='', default='')
    filename_spatialmos_spread_md = models.ImageField(upload_to='', default='')
    filename_spatialmos_spread_lg = models.ImageField(upload_to='', default='')

    def __str__(self):
        """Return Value in the Admin Panel"""
        return "{} | Valid: {} | Step: {:03d}".format(self.spatialmos_run, self.valid_date.strftime("%Y-%m-%d %H:%M"), self.step)

    class Meta:
        """Settings"""
        ordering = ("spatialmos_run", "step")


class SpatialMosPoint(models.Model):
    """The model for a spatiaMOS Point"""
    spatialmos_step = models.ForeignKey(SpatialMosStep, related_name="points", on_delete=models.CASCADE)
    lat = models.DecimalField(max_digits=16, decimal_places=14, default=None)
    lon = models.DecimalField(max_digits=16, decimal_places=14, default=None)
    spatialmos_mean = models.DecimalField(max_digits=6, decimal_places=2, default=None)
    spatialmos_spread = models.DecimalField(max_digits=6, decimal_places=2, default=None)

    def __str__(self):
        """Return Value in the Admin Panel"""
        return f"{self.spatialmos_step} | Location: {self.lat}, {self.lon} | mean: {self.spatialmos_mean} spread: {self.spatialmos_spread}"

    class Meta:
        """Settings"""
        ordering = ("spatialmos_step", "-lat", "lon")
        indexes = [
            models.Index(fields=['spatialmos_step', 'lat', 'lon'])
        ]
