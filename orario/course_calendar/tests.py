from datetime import time
from django.test import TestCase
from models import *
from scheduler.models import *


class CourseTestCase(TestCase):
    def setUp(self):
        self.c1 = Course.objects.create(
            number='COMP 248',
            title='No coreqs',
            credits=3)
        self.c2 = Course.objects.create(
            number='COMP 249',
            title="Let's say COMP 248 is a coreq",
            credits=3)
        self.c2.coreqs.add(self.c1)

    def test_is_coreq_for_success(self):
        self.assertTrue(self.c1.is_coreq_for(self.c2))

    def test_is_coreq_for_fail(self):
        self.assertFalse(self.c2.is_coreq_for(self.c1))


class SectionTestCase(TestCase):
    def setUp(self):
        ## Here we stub a bunch of courses.
        self.c1 = Course.objects.create(
            number='COMP 248',
            title='Has no tut nor lab, conflicts with tutorial from c2',
            credits=3)
        self.c2 = Course.objects.create(
            number='COMP 249',
            title='Has tut but no lab, conflicts with lect from c1 and lab from c3',
            credits=3)
        self.c3 = Course.objects.create(
            number='COMP 240',
            title='Has tut and lab, no conflict with c1',
            credits=3)

        self.lec_c1 = LectureSlot.objects.create(
            label="",
            begin_time=time(8, 45),
            end_time=time(10, 00),
            days=WEDNESDAY | FRIDAY,
            section_code="AA",
            instructor="Gangnam Style",
            room="SGW H820"
        )

        self.lec_c2 = LectureSlot.objects.create(
            label="",
            begin_time=time(13, 00),
            end_time=time(14, 15),
            days=MONDAY | WEDNESDAY,
            section_code="BB",
            instructor="PSY",
            room="SGW H820"
        )
        self.tut_c2 = TutorialSlot.objects.create(
            label="",
            begin_time=time(9, 45),
            end_time=time(11, 00),
            days=TUESDAY | FRIDAY,
            section_code="BB",
            instructor="PSY",
            room="SGW H820"
        )

        self.lec_c3 = LectureSlot.objects.create(
            label="",
            begin_time=time(16, 15),
            end_time=time(17, 30),
            days=TUESDAY | THURSDAY,
            section_code="CC",
            instructor="PSY",
            room="SGW H720"
        )
        self.tut_c3 = TutorialSlot.objects.create(
            label="",
            begin_time=time(17, 45),
            end_time=time(18, 40),
            days=THURSDAY,
            section_code="CC",
            instructor="PSY",
            room="SGW H720"
        )
        self.lab_c3 = LabSlot.objects.create(
            label="",
            begin_time=time(9, 45),
            end_time=time(12, 30),
            days=TUESDAY,
            section_code="CC",
            instructor="PSY",
            room="SGW H720"
        )

        self.sec1_c1 = Section.objects.create(
            course=self.c1,
            lecture=self.lec_c1
        )
        self.sec2_c2 = Section.objects.create(
            course=self.c2,
            lecture=self.lec_c2,
            tutorial=self.tut_c2
        )
        self.sec3_c3 = Section.objects.create(
            course=self.c3,
            lecture=self.lec_c3,
            tutorial=self.tut_c3,
            lab=self.lab_c3
        )

    def test_conflicts_with_time_slot(self):
        self.assertTrue(self.sec1_c1.conflicts_with(self.tut_c2))

    def test_conflicts_with_sec_tut_lab(self):
        self.assertTrue(self.sec2_c2.conflicts_with(self.sec3_c3))

    def test_conflicts_with_sec_tut_no_lab(self):
        self.assertTrue(self.sec1_c1.conflicts_with(self.sec2_c2))

    def test_conflicts_with_sec_no_tut_no_lab(self):
        self.assertFalse(self.sec3_c3.conflicts_with(self.sec1_c1))