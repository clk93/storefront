from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class Tag(models.Model):
    label = models.CharField(max_length=255)

 # What Tag applied to what Object (Video, Order, etc) -> Generic relationships
class TagItem(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    # Use ContentType to allow generic relationships 
    # Type (product, article, video, etc) -> table
    # ID -> record (primary key)
    # conent_object = read the object that a particular tag os applied to
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
