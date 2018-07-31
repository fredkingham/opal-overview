from decimal import Decimal, getcontext
from django.db.models import Count
from django.db.models.functions import Lower
from django.utils.functional import cached_property
from opal.core import subrecords


class Field(object):
    @property
    def template(self):
        raise NotImplementedError(
            "please implement a template"
        )

    def __init__(self, episodes, model, field_name):
        self.episodes = episodes
        self.model = model
        self.field_name = field_name

    def display_name(self):
        return self.model._get_field_title(self.field_name)

    def model_qs(self):
        if self.model in subrecords.patient_subrecords():
            patient_ids = self.episodes.values_list(
                'patient_id', flat=True
            ).distinct()
            return self.model.objects.filter(patient_id__in=patient_ids)
        else:
            episode_ids = self.episodes.values_list('id', flat=True)
            return self.model.objects.filter(episode_id__in=episode_ids)


class DefaultField(Field):
    template = "overview/fields/default_field.html"

    def total_populated(self):
        return self.model_qs().exclude(**{self.field_name: None}).count()

    def percentage_populated(self):
        total_count = self.model_qs().count()
        if total_count == 0:
            return 0
        getcontext().prec = 2
        return (Decimal(self.total_populated())/total_count) * 100


class ForeignKeyOrFreeTextField(DefaultField):
    template = "overview/fields/fk_or_ft.html"
    TOP_AMOUNT = 10

    @property
    def free_text_field_name(self):
        return "{}_ft".format(self.field_name)

    @property
    def foreign_key_id_field_name(self):
        return "{}_fk_id".format(self.field_name)

    def total_populated(self):
        unpopulated = self.model_qs().filter(
            **{self.free_text_field_name: ''}
        ).filter(
            **{self.foreign_key_id_field_name: None}
        )
        return self.model_qs().count() - unpopulated.count()

    @cached_property
    def top_uncoded(self):
        """
        Returns the top ft results in reverse.

        As a list of lists where list[0] is the ft
        and list[1] is the amount
        """
        qs = self.model_qs().exclude(**{self.free_text_field_name: ''})
        top_ft = qs.annotate(
            lower_ft_field=Lower(self.free_text_field_name)
        )
        top_ft = top_ft.values("lower_ft_field")
        top_ft = top_ft.annotate(
            counted_ft_field=Count("lower_ft_field")
        )
        top_ft = top_ft.order_by("-counted_ft_field")[:self.TOP_AMOUNT]

        return top_ft.values_list("lower_ft_field", "counted_ft_field")

    @cached_property
    def top_coded(self):
        """
        Returns the top ft results in reverse.

        As a list of lists where list[0] is the ft
        and list[1] is the amount
        """
        qs = self.model_qs().exclude(**{self.foreign_key_id_field_name: None})

        fk_id = qs.values(self.foreign_key_id_field_name)
        fk_id = fk_id.annotate(
            counted_fk_field=Count(self.foreign_key_id_field_name)
        )
        fk_id = fk_id.order_by("-counted_fk_field")[:self.TOP_AMOUNT]

        return fk_id.values_list(
            "{}_fk__name".format(self.field_name), "counted_fk_field"
        )
