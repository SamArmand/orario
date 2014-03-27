from django.test import TestCase
from models import *

from datetime import time

class TimeSlotTestCase(TestCase):
    """
    Run these tests by running manage.py test
    """
    def setUp(self):
        """
        Inserts dummy data into the database for testing.
        """
        LectureSlot.objects.create(
            label="",
            begin_time=time(8, 45),
            end_time=time(10, 00),
            days=WEDNESDAY|FRIDAY,  # Bitwise or to set both wed and fri bits to 1
            section_code="AA",
            instructor="Gangnam Style",
            room="SGW H820"
        )

        LectureSlot.objects.create(
            label="",
            begin_time=time(9, 45),
            end_time=time(11, 00),
            days=TUESDAY|FRIDAY,  # Bitwise or to set both wed and fri bits to 1
            section_code="BB",
            instructor="PSY",
            room="SGW H820"
        )

        LectureSlot.objects.create(
            label="",
            begin_time=time(9, 45),
            end_time=time(11, 00),
            days=TUESDAY|THURSDAY,  # Bitwise or to set both wed and fri bits to 1
            section_code="CC",
            instructor="PSY",
            room="SGW H820"
        )

        LectureSlot.objects.create(
            label="",
            begin_time=time(10, 15),
            end_time=time(11, 30),
            days=WEDNESDAY|FRIDAY,  # Bitwise or to set both wed and fri bits to 1
            section_code="DD",
            instructor="PSY",
            room="SGW H820"
        )

    def test_time_conflict(self):
        lect0 = LectureSlot.objects.get(section_code="AA")
        lect1 = LectureSlot.objects.get(section_code="BB")
        self.assertTrue(lect0.conflicts_with(lect1))
        self.assertTrue(lect1.conflicts_with(lect0))