from django.utils import timezone
from opal.core.test import OpalTestCase
from opal import models as omodels
from opal.tests.models import (
    FavouriteNumber,  # patient subrecord
    FavouriteColour,  # patient singleton
    HoundOwner,  # episode subrecord
    EpisodeName,  # episode singleton
)
from overview import overview_utils


class GetSubrecordUseTestCase(OpalTestCase):
    def setUp(self):
        self.patient_1, self.episode_1 = self.new_patient_and_episode_please()
        self.patient_2, self.episode_2 = self.new_patient_and_episode_please()
        self.episode_3 = self.patient_2.create_episode()

    def test_episode_none(self):
        """
        If there is a single episode then we should use
        that
        """
        result = overview_utils.get_subrecord_use(
            HoundOwner,
            omodels.Episode.objects.all(),
        )
        self.assertFalse(result.exists())

    def test_episode_one(self):
        """
        test we work correctly with multiple episodes
        each with its own episode
        """
        ho1 = HoundOwner.objects.create(episode=self.episode_1)
        ho2 = HoundOwner.objects.create(episode=self.episode_2)
        HoundOwner.objects.create(episode=self.episode_3)
        episode_qs = omodels.Episode.objects.exclude(id=self.episode_3.id)
        result = overview_utils.get_subrecord_use(
            HoundOwner,
            episode_qs,
        )
        self.assertEqual(result.count(), 2)
        self.assertEqual(result[0], ho1)
        self.assertEqual(result[1], ho2)

    def test_episode_multiple(self):
        """ test we work correctly when we have the same episode
            with mutiple subrecords
        """
        ho1 = HoundOwner.objects.create(episode=self.episode_1)
        ho2 = HoundOwner.objects.create(episode=self.episode_1)
        HoundOwner.objects.create(episode=self.episode_2)
        episode_qs = omodels.Episode.objects.filter(id=self.episode_1.id)
        result = overview_utils.get_subrecord_use(
            HoundOwner,
            episode_qs,
        )
        self.assertEqual(result.count(), 2)
        self.assertEqual(result[0], ho1)
        self.assertEqual(result[1], ho2)

    def test_episode_singleton(self):
        EpisodeName.objects.all().update(
            created=timezone.now(), updated=timezone.now()
        )
        episode_qs = omodels.Episode.objects.exclude(id=self.episode_3.id)
        result = overview_utils.get_subrecord_use(
            EpisodeName,
            episode_qs,
        )
        self.assertEqual(result.count(), 2)
        self.assertEqual(result[0], self.episode_1.episodename_set.first())
        self.assertEqual(result[1], self.episode_2.episodename_set.first())

    def test_episode_singleton_not_updated(self):
        EpisodeName.objects.create(episode=self.episode_1)
        episode_qs = omodels.Episode.objects.all()
        result = overview_utils.get_subrecord_use(
            EpisodeName,
            episode_qs,
        )
        self.assertFalse(result.exists())

    def test_patient_none(self):
        episode_qs = omodels.Episode.objects.all()
        result = overview_utils.get_subrecord_use(
            FavouriteNumber,
            episode_qs,
        )
        self.assertFalse(result.exists())

    def test_patient_one(self):
        b1 = FavouriteNumber.objects.create(patient=self.patient_1)
        b2 = FavouriteNumber.objects.create(patient=self.patient_1)

        # the below won't be used
        FavouriteNumber.objects.create(patient=self.patient_2)

        episode_qs = omodels.Episode.objects.filter(id=self.episode_1.id)
        result = overview_utils.get_subrecord_use(
            FavouriteNumber,
            episode_qs,
        )
        self.assertEqual(result.count(), 2)
        self.assertEqual(result[0], b1)
        self.assertEqual(result[1], b2)

    def test_patient_singleton(self):
        FavouriteColour.objects.all().update(
            created=timezone.now(), updated=timezone.now()
        )
        episode_qs = omodels.Episode.objects.exclude(id=self.episode_3.id)
        result = overview_utils.get_subrecord_use(
            FavouriteColour,
            episode_qs,
        )
        self.assertEqual(result.count(), 2)
        self.assertEqual(
            result[0], self.episode_1.patient.favouritecolour_set.first()
        )
        self.assertEqual(
            result[1], self.episode_2.patient.favouritecolour_set.first()
        )


class GetProbabilityAnEpisodeUsesASubrecord(OpalTestCase):
    def setUp(self):
        self.patient_1, self.episode_1 = self.new_patient_and_episode_please()
        self.patient_2, self.episode_2 = self.new_patient_and_episode_please()
        self.episode_3 = self.patient_2.create_episode()

    def test_episode(self):
        HoundOwner.objects.create(episode=self.episode_1)
        HoundOwner.objects.create(episode=self.episode_1)
        result = overview_utils.get_probability_an_episode_uses_a_subrecord(
            HoundOwner.objects.all(),
            omodels.Episode.objects.all(),
        )
        self.assertEqual(
            result, 33.33
        )

    def test_patient(self):
        FavouriteNumber.objects.create(patient=self.patient_2)
        result = overview_utils.get_probability_an_episode_uses_a_subrecord(
            FavouriteNumber.objects.all(),
            omodels.Episode.objects.all(),
        )
        self.assertEqual(
            result, 66.67
        )

    def test_singleton(self):
        EpisodeName.objects.filter(episode=self.episode_1).update(
            created=timezone.now(), updated=timezone.now()
        )
        result = overview_utils.get_probability_an_episode_uses_a_subrecord(
            EpisodeName.objects.exclude(updated=None),
            omodels.Episode.objects.all(),
        )
        self.assertEqual(
            result, 33.33
        )


class GetTopFtTestCase(OpalTestCase):
    def setUp(self, *args, **kwargs):
        super(GetTopFtTestCase, self).setUp(*args, **kwargs)
        self.patient_1, self.episode_1 = self.new_patient_and_episode_please()
        self.patient_2, self.episode_2 = self.new_patient_and_episode_please()
        self.episode_3 = self.patient_2.create_episode()

    def test_get_top_episode_subrecord_ft(self):
        ho_1 = HoundOwner.objects.create(
            episode=self.episode_1
        )
        ho_1.dog = "alsation"
        ho_1.save()

        ho_2 = HoundOwner.objects.create(
            episode=self.episode_2
        )
        ho_2.dog = "Alsation"
        ho_2.save()

        ho_3 = HoundOwner.objects.create(
            episode=self.episode_2
        )
        ho_3.dog = "basset"
        ho_3.save()

        result = overview_utils.get_top_ft(
            HoundOwner.objects.all(),
            "dog",
            omodels.Episode.objects.all(),
            amount=3
        )

        self.assertEqual(
            len(result), 2
        )
        self.assertEqual(
            result[0][0], "alsation"
        )
        self.assertEqual(
            result[0][1], 2
        )
        self.assertEqual(
            result[0][2], 66.67
        )

        self.assertEqual(
            result[1][0], "basset"
        )
        self.assertEqual(
            result[1][1], 1
        )
        self.assertEqual(
            result[1][2], 33.33
        )
