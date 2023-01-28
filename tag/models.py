from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

class TagItemManager(models.Manager):
    def get_tags_for(self, obj_type, obj_id):
        content_type = ContentType.objects.get_for_model(obj_type)
        return TagItem.objects\
                .select_related('tag')\
                .filter(
                    content_type = content_type,
                    object_id= obj_id
                )


class Tag(models.Model):
    label = models.CharField(max_length=255)
    def __str__(self) -> str:
        return self.label

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
    objects = TagItemManager()
