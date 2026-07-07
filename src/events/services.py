from datetime import timedelta
from django.contrib.contenttypes.models import ContentType
from django.db.models.functions import Coalesce
from django.db.models import Count, Q
from django.utils import timezone
from .models import Event


def get_event_analytics(content_object, gapfill=False, ignore_type=[]):
    if not hasattr(content_object, "id") or not hasattr(content_object, "__class__"):
        return None

    ModelKlass = content_object.__class__
    ctype = ContentType.objects.get_for_model(ModelKlass)
    now = timezone.now()
    oldest_time = now - timedelta(hours=72)

    chunk_time = "1 hour"
    # events wont exist before object creation
    if hasattr(content_object, "created_at"):
        oldest_time = content_object.created_at

    start_date = oldest_time
    end_date = now
    dataset_range = (oldest_time, now)

    event_type_annotations = {}
    for _event_type in Event.EventType.values:
        if _event_type not in ignore_type:
            event_type_annotations[f"{_event_type}_count"] = Coalesce(
                Count("id", filter=Q(type=_event_type)), 0
            )

    if gapfill:
        dataset = (
            Event.timescale.filter(
                time__range=dataset_range,
                content_type=ctype,
                object_id=content_object.id,
            )
            .exclude(type__in=ignore_type)
            .time_bucket_gapfill("time", chunk_time, start_date, end_date)
            .values("bucket")
            .annotate(**event_type_annotations)
            .order_by("bucket")
        )
    else:
        dataset = (
            Event.timescale.filter(
                time__range=dataset_range,
                content_type=ctype,
                object_id=content_object.id,
            )
            .exclude(type__in=ignore_type)
            .time_bucket("time", chunk_time)
            .values("bucket")
            .annotate(**event_type_annotations)
            .order_by("bucket")
        )

    return dataset
