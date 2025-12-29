from django.db import models
    
class DownloadedVideo(models.Model):
    url = models.CharField(max_length=200)
    
    video_title = models.CharField(max_length=100)
    video_path = models.FilePathField()
    video_length_s = models.PositiveIntegerField()
    video_file_size_b = models.PositiveBigIntegerField()

    created_at = models.DateField()

    def __str__(self):
        return self.video_title