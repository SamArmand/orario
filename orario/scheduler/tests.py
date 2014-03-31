from django.test import TestCase
from models import *
from student.models import *
from course_calendar.models import *

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

    def test_time_no_conflict(self):
        lect0 = LectureSlot.objects.get(section_code="AA")
        lect1 = LectureSlot.objects.get(section_code="CC")
        lect2 = LectureSlot.objects.get(section_code="DD")
        self.assertFalse(lect0.conflicts_with(lect1))
        self.assertFalse(lect1.conflicts_with(lect0))
        self.assertFalse(lect0.conflicts_with(lect2))
        self.assertFalse(lect2.conflicts_with(lect0))

        
class AddCourseTestCase(TestCase):
    def setUp(self):
        """
        Inserts dummy data into the databse fo testing.
        """
        # create_user is a helper method from the django AbstractUser class which Student inherits
        self.student1 = Student.objects.create_user('test', 'test@test.com', 'testpassword')
        self.student2 = Student.objects.create_user('test2', 'test2@test.com', 'testpassword')
        self.schedule1 = Schedule.objects.create(
            student=self.student1,
            term=2)
        self.schedule2 = Schedule.objects.create(
            student=self.student2,
            term=2)
        self.course1 = Course.objects.create(
            number='COMP 248',
            title='Java 1',
            credits=3)
        self.course2 = Course.objects.create(
            number='COMP 249',
            title='Java 2',
            credits=3)
        self.course2.prereqs.add(self.course1)
        self.student1.courses_taken.add(self.course1)
    
    def test_add_course_success(self):
        """
        self.schedule1 belongs to student1, who has taken COMP 248.
        """
        legit = self.schedule1.add_course(self.course2)
        self.assertTrue(legit)
    
    def test_add_course_fail(self):
        """
        self.schedule2 belongs to student2, who has NOT taken COMP 248. Therefore adding COMP 249 should fail.
        """
        fail = self.schedule2.add_course(self.course2)
        self.assertFalse(fail)



class RemoveCourseTestCase(TestCase):
    def setUp(self):
        self.schedule1 = Schedule.objects.create(
            student=self.student1,
            term=2)
        self.course1 = Course.objects.create(
            number='COMP 248',
            title='Java 1',
            credits=3)
        self.course2 = Course.objects.create(
            number='COMP 248',
            title='Java 1',
            credits=3)
            