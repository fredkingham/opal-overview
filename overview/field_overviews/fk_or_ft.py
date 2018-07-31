from overview import overview_utils
from django.db.models.functions import Lower
from django.db.models import Count


def get_field_dict(episode_qs, model, field_name):
    field_dict = dict(
        display_name=model.field,
        template="overview/fields/fk_or_ft.html",
        context={}
    )
    subrecord_qs = overview_utils.get_subrecord_use(model, episode_qs)
    field_dict["context"]["top_ft"] = get_top_ft(
        subrecord_qs, field_name, episode_qs
    )
    return field_dict


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


def get_top_ft(qs, field_name, episode_qs, amount=25):
    """
    Gets a summary of the top 25 ft fields of the amount.
    """
    ft_field = "{}_ft".format(field_name)
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
        result.append(overview_utils.get_summary_row(
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
