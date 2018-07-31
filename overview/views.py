"""
Views for the overview Opal Plugin
"""
from django.contrib.auth import mixins
from django.views.generic import TemplateView

from opal.core import subrecords
from opal import models as omodels
from opal.core.fields import ForeignKeyOrFreeText

from overview import overview_utils
from overview import fields


class SuperUserRequired(mixins.UserPassesTestMixin):
    def test_func(self):
        """
        Override this method to use a different test_func method.
        """
        return self.request.user.is_authenticated() and self.request.user.is_superuser


class OverviewListView(SuperUserRequired, TemplateView):
    template_name = "overview/list.html"

    def get_episode_qs(self):
        return omodels.Episode.objects.all()

    def get_context_data(self, *args, **kwargs):
        ctx = super(OverviewListView, self).get_context_data(
            *args, **kwargs
        )
        episode_qs = self.get_episode_qs()

        ctx["subrecords"] = []

        for subrecord in subrecords.subrecords():
            qs = overview_utils.get_subrecord_use(
                subrecord, episode_qs,
            )
            ctx["subrecords"].append((
                overview_utils.get_summary_row(
                    subrecord, qs, episode_qs
                )
            ))

        ctx["subrecords"] = sorted(ctx["subrecords"], key=lambda x: x[0])
        ctx["subrecords"] = sorted(ctx["subrecords"], key=lambda x: -x[1])
        ctx["subrecords"] = sorted(ctx["subrecords"], key=lambda x: -x[2])
        return ctx


class OverviewDetailView(SuperUserRequired, TemplateView):
    template_name = "overview/subrecord.html"

    IGNORED_FIELDS = {
        "id",
        "created",
        "updated",
        "created_by_id",
        "updated_by_id",
        "consistency_token",
        "episode_id",
        "patient_id"
    }

    def get_episode_qs(self):
        return omodels.Episode.objects.all()

    def get_ft_or_fk_detail(self, qs, field, episode_qs):
        # so for ft_or_fk we want, the % the field is populated
        # the top 10 fk populated options with the % of subrecords that this
        # the top 10 ft populated options with the % of subrecords that this
        fk_field = "{}_fk".format(field)
        ft_field = "{}_ft".format(field)

        result = {}
        result["count"] = qs.count()
        result["number_none"] = qs.filter(
            **{ft_field: ""}
        ).filter(
            **{fk_field: None}
        ).count()

        result["top_ten_ft"] = dict(
            top_ten=overview_utils.get_top_25_ft(qs, field, episode_qs)
        )
        return result

    def get_context_data(self, *args, **kwargs):
        ctx = super(OverviewDetailView, self).get_context_data(*args, **kwargs)
        episode_qs = self.get_episode_qs()
        subrecord = subrecords.get_subrecord_from_api_name(kwargs["api_name"])
        ctx["fields"] = []
        for field_name in subrecord._get_fieldnames_to_serialize():
            if field_name in self.IGNORED_FIELDS:
                continue

            field = subrecord._get_field(field_name)
            if isinstance(field, ForeignKeyOrFreeText):
                ctx["fields"].append(
                    fields.ForeignKeyOrFreeTextField(episode_qs, subrecord, field_name)
                )
            else:
                ctx["fields"].append(
                    fields.DefaultField(episode_qs, subrecord, field_name)
                )
        ctx["subrecord"] = subrecord
        return ctx
