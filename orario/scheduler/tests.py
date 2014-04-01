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

        
class ScheduleTestCase(TestCase):
    def setUp(self):
        """
        Inserts dummy data into the databse fo testing.
        """
        ## Here we add stub objects for the add course test case
        # create_user is a helper method from the django AbstractUser class which Student inherits
        self.student_add1 = Student.objects.create_user('test', 'test@test.com', 'testpassword')
        self.student_add2 = Student.objects.create_user('test2', 'test2@test.com', 'testpassword')
        self.schedule_add1 = Schedule.objects.create(
            student=self.student_add1,
            term=2)
        self.schedule_add2 = Schedule.objects.create(
            student=self.student_add2,
            term=2)
        self.course_add1 = Course.objects.create(
            number='COMP 248',
            title='Java 1',
            credits=3)
        self.course_add2 = Course.objects.create(
            number='COMP 249',
            title='Java 2',
            credits=3)
        self.course_add3 = Course.objects.create(
            number='COMP 240',
            title='Imaginary course that coreqs Java 1',
            credits=3)
        self.course_add2.prereqs.add(self.course_add1)
        self.course_add3.coreqs.add(self.course_add1)
        self.student_add1.courses_taken.add(self.course_add1)

        ## Here we add stub objects for the remove course test case
        self.student_remove1 = Student.objects.create_user('test3', 'test3@test.com', 'testpassword')
        self.schedule_remove1 = Schedule.objects.create(
            student=self.student_remove1,
            term=2)
        self.course_remove1 = Course.objects.create(
            number='COMP 371',
            title='Computer Graphics',
            credits=3)
        self.course_remove2 = Course.objects.create(
            number='COMP 376',
            title='Intro to Game Developement',
            credits=3)
        self.course_remove2.coreqs.add(self.course_remove1)
    
    def test_add_course_prereq_success(self):
        """
        self.schedule_add1 belongs to student1, who has taken COMP 248.
        """
        legit = self.schedule_add1.add_course(self.course_add2)
        self.assertTrue(legit)
    
    def test_add_course_prereq_fail(self):
        """
        self.schedule_add2 belongs to student2, who has NOT taken COMP 248. Therefore adding COMP 249 should fail.
        """
        fail = self.schedule_add2.add_course(self.course_add2)
        self.assertFalse(fail)

    def test_add_course_coreq_success(self):
        """
        self.schedule_add1 belongs to student1, who has taken COMP 248.
        """
        legit = self.schedule_add1.add_course(self.course_add3)
        self.assertTrue(legit)

    def test_add_course_coreq_fail(self):
        """
        self.schedule_add2 belongs to student2, who has NOT taken COMP 248. Therefore adding COMP 240 should fail.
        """
        fail = self.schedule_add2.add_course(self.course_add3)
        self.assertFalse(fail)
    
    def test_remove_course_typical(self):
        """
        course_remove2 depends on course_remove1, so removing 2 should not remove 1.
        """
        # Force add the two courses
        self.schedule_remove1.courses.add(self.course_remove1)
        self.schedule_remove1.courses.add(self.course_remove2)
        # Remove the dependent course
        self.schedule_remove1.remove_course(self.course_remove2)
        # self.schedule1 should not contain course2, but it should still contain course1.
        legitTrue = self.course_remove1 in self.schedule_remove1.courses.all()
        legitFalse = self.course_remove2 in self.schedule_remove1.courses.all()
        self.assertTrue(legitTrue)
        self.assertFalse(legitFalse)
        self.schedule_remove1.courses.clear()

    def test_remove_course_coreq(self):
        """
        course_remove1 depends on course_remove2, so removing 1 should remove 2.
        """
        self.schedule_remove1.courses.add(self.course_remove1)
        self.schedule_remove1.courses.add(self.course_remove2)
        # Testing the removal of the corequisite course
        self.schedule_remove1.remove_course(self.course_remove1)
        # self.schedule1 should not contain course1.
        legitFalse1 = self.course_remove1 in self.schedule_remove1.courses.all()
        # self.schedule1 should not contain course2.
        legitFalse2 = self.course_remove2 in self.schedule_remove1.courses.all()
        self.assertFalse(legitFalse1)
        self.assertFalse(legitFalse2)
        self.schedule_remove1.courses.clear()
