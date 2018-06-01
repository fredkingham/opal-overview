from decimal import Decimal
from django.db.models.functions import Lower
from django.db.models import Count
from opal.core import subrecords

TOP_AMOUNT = 25


def get_subrecord_use(subrecord, episode_qs):
    """
    Get's all populated subrecords in an episode_qs.
    For singletons, populated means they have an updated flag
    """
    is_episode_subrecord = subrecord in subrecords.episode_subrecords()
    if subrecord._is_singleton:
        populated = subrecord.objects.exclude(updated=None)
    else:
        populated = subrecord.objects.all()

    if is_episode_subrecord:
        return populated.filter(episode__in=episode_qs).distinct()
    else:
        return populated.filter(patient__episode__in=episode_qs).distinct()


def get_probability_an_episode_uses_a_subrecord(
    subrecord_qs, episode_qs
):
    """
    Given an episode queryset and a subrecord queryset,
    give me the probability that a given episode has a given subrecord.

    (some episodes could have more than one subrecord)
    """
    subrecord = subrecord_qs.model
    is_episode_subrecord = subrecord in subrecords.episode_subrecords()
    if is_episode_subrecord:
        id_count = subrecord_qs.values_list(
            "episode_id", flat=True
        ).distinct().count()
    else:
        id_count = subrecord_qs.values_list(
            "patient__episode", flat=True
        ).distinct().count()
    return round(Decimal(id_count)/episode_qs.count() * 100, 2)


def get_summary_row(display_name, subrecord_qs, episode_qs):
    """
    A summary row is a
        * Thedisplay name of a subrecord, or a field value.
        * The total count of subrecords
        * The probability that an episode in that qs has that value
    """
    return (
        display_name,
        subrecord_qs.count(),
        get_probability_an_episode_uses_a_subrecord(
            subrecord_qs, episode_qs
        ),
    )


def get_ft_display_name(
    subrecord_qs, ft_field_name, ft_field_value
):
    """
    When aggregating free text we ignore case.

    This gives us the first populated value from the qs
    that is case sensitive.
    """
    return getattr(
        subrecord_qs.filter(**{ft_field_name: ft_field_value}).first(),
        ft_field_name
    )


def get_top_ft(qs, field, episode_qs, amount=25):
    """
    Gets a summary of the top 25 ft fields of the amount.
    """
    ft_field = "{}_ft".format(field)
    top_ft = qs.annotate(
        lower_ft_field=Lower(ft_field)
    )

    top_ft = top_ft.values("lower_ft_field")

    top_ft = top_ft.annotate(
        counted_ft_field=Count("lower_ft_field")
    )
    top_ft = top_ft.order_by("-counted_ft_field")[:amount]
    result = []

    for row in top_ft:
        result.append(get_summary_row(
            get_ft_display_name(qs, ft_field, row["lower_ft_field"]),
            qs.filter(
                **{"{}__iexact".format(ft_field): row["lower_ft_field"]}
            ),
            episode_qs
        ))

    result = sorted(result, key=lambda x: x[0])
    result = sorted(result, key=lambda x: -x[1])
    result = sorted(result, key=lambda x: -x[2])

    return result
