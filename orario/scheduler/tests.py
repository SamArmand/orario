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

    def test_conflicts_with_success(self):
        lect0 = LectureSlot.objects.get(section_code="AA")
        lect1 = LectureSlot.objects.get(section_code="BB")
        self.assertTrue(lect0.conflicts_with(lect1))

    def test_conflicts_with_fail_days(self):
        lect0 = LectureSlot.objects.get(section_code="AA")
        lect1 = LectureSlot.objects.get(section_code="CC")
        self.assertFalse(lect0.conflicts_with(lect1))

    def test_conflicts_with_fail_hours(self):
        lect0 = LectureSlot.objects.get(section_code="AA")
        lect1 = LectureSlot.objects.get(section_code="DD")
        self.assertFalse(lect0.conflicts_with(lect1))


class ScheduleTestCase(TestCase):
    def setUp(self):
        """
        Inserts dummy data into the databse fo testing.
        """
        ## Here we stub a bunch of courses.
        # create_user is a helper method from the django AbstractUser class which Student inherits
        self.c1 = Course.objects.create(
            number='COMP 248',
            title='Java 1',
            credits=3)
        self.c2_pre_c1 = Course.objects.create(
            number='COMP 249',
            title='Java 2',
            credits=3)
        self.c3_co_c1 = Course.objects.create(
            number='COMP 240',
            title='Imaginary course that coreqs Java 1',
            credits=3)
        self.c2_pre_c1.prereqs.add(self.c1)
        self.c3_co_c1.coreqs.add(self.c1)

        ## Here we add stub sections for the add/remove section test cases
        self.lec1_c1 = LectureSlot.objects.create(
            label="",
            begin_time=time(8, 45),
            end_time=time(10, 00),
            days=WEDNESDAY|FRIDAY,  # Bitwise or to set both wed and fri bits to 1
            section_code="AA",
            instructor="Gangnam Style",
            room="SGW H820"
        )
        self.lec2_c2 = LectureSlot.objects.create(
            label="",
            begin_time=time(9, 45),
            end_time=time(11, 00),
            days=TUESDAY|FRIDAY,  # Bitwise or to set both wed and fri bits to 1
            section_code="BB",
            instructor="PSY",
            room="SGW H820"
        )
        self.lec3_c3 = LectureSlot.objects.create(
            label="",
            begin_time=time(9, 45),
            end_time=time(11, 00),
            days=TUESDAY|THURSDAY,  # Bitwise or to set both wed and fri bits to 1
            section_code="CC",
            instructor="PSY",
            room="SGW H820"
        )
        self.sec1_c1 = Section.objects.create(
            course=self.c1,
            lecture=self.lec1_c1
        )
        self.sec2_c2 = Section.objects.create(
            course=self.c2_pre_c1,
            lecture=self.lec2_c2
        )
        self.sec3_c3 = Section.objects.create(
            course=self.c3_co_c1,
            lecture=self.lec3_c3
        )

    def test_add_course_typical(self):
        """
        Typical case, just add a course with no prereqs or coreqs.
        """
        student = Student.objects.create_user('test_add_course_typical', 'test@test.com', 'testpassword')
        schedule = Schedule.objects.create(
            student=student,
            term=2)
        result = schedule.add_course(self.c1)
        self.assertTrue(result)  # return value
        self.assertTrue(self.c1 in schedule.courses.all())  # postcondition

    def test_add_course_prereq_success(self):
        """
        self.schedule_add1 belongs to student1, who has taken COMP 248.
        """
        student = Student.objects.create_user('test_add_course_prereq_success', 'test@test.com', 'testpassword')
        schedule = Schedule.objects.create(
            student=student,
            term=2)
        student.courses_taken.add(self.c1)
        result = schedule.add_course(self.c2_pre_c1)
        self.assertTrue(result)
        self.assertTrue(self.c2_pre_c1 in schedule.courses.all())

    def test_add_course_prereq_fail(self):
        """
        self.schedule_add2 belongs to student2, who has NOT taken COMP 248. Therefore adding COMP 249 should fail.
        """
        student = Student.objects.create_user('test_add_course_prereq_fail', 'test@test.com', 'testpassword')
        schedule = Schedule.objects.create(
            student=student,
            term=2)
        result = schedule.add_course(self.c2_pre_c1)
        self.assertFalse(result)  # return value
        self.assertFalse(self.c2_pre_c1 in schedule.courses.all())  # postcondition

    def test_add_course_coreq_success(self):
        """
        self.schedule_add1 belongs to student1, who has taken COMP 248.
        """
        student = Student.objects.create_user('test_add_course_coreq_success', 'test@test.com', 'testpassword')
        schedule = Schedule.objects.create(
            student=student,
            term=2)
        schedule.courses.add(self.c1)
        result = schedule.add_course(self.c3_co_c1)
        self.assertTrue(result)  # return value
        self.assertTrue(self.c3_co_c1 in schedule.courses.all())  # postcondition

    def test_add_course_coreq_fail(self):
        """
        self.schedule_add2 belongs to student2, who has NOT taken COMP 248. Therefore adding COMP 240 should fail.
        """
        student = Student.objects.create_user('test_add_course_coreq_fail', 'test@test.com', 'testpassword')
        schedule = Schedule.objects.create(
            student=student,
            term=2)
        result = schedule.add_course(self.c3_co_c1)
        self.assertFalse(result)  # return value
        self.assertFalse(self.c3_co_c1 in schedule.courses.all())  # postcondition

    def test_remove_course_typical(self):
        """
        course_remove2 depends on course_remove1, so removing 2 should not remove 1.
        """
        # Force add the two courses
        student = Student.objects.create_user('test_remove_course_typical', 'test@test.com', 'testpassword')
        schedule = Schedule.objects.create(
            student=student,
            term=2)
        schedule.courses.add(self.c1)
        schedule.courses.add(self.c3_co_c1)
        # Remove the dependent course
        schedule.remove_course(self.c3_co_c1)
        # self.schedule1 should not contain course2, but it should still contain course1.
        self.assertTrue(self.c1 in schedule.courses.all())
        self.assertFalse(self.c3_co_c1 in schedule.courses.all())

    def test_remove_course_coreq(self):
        """
        course_remove1 depends on course_remove2, so removing 1 should remove 2.
        """
        student = Student.objects.create_user('test_remove_course_coreq', 'test@test.com', 'testpassword')
        schedule = Schedule.objects.create(
            student=student,
            term=2)
        schedule.courses.add(self.c1)
        schedule.courses.add(self.c3_co_c1)
        # Testing the removal of the corequisite course
        schedule.remove_course(self.c1)
        # self.schedule1 should not contain course1.
        # self.schedule1 should not contain course2.
        self.assertFalse(self.c1 in schedule.courses.all())
        self.assertFalse(self.c3_co_c1 in schedule.courses.all())

    def test_add_section_typical(self):
        student = Student.objects.create_user('test_add_section_typical', 'test@test.com', 'testpassword')
        schedule = Schedule.objects.create(
            student=student,
            term=2)
        # Simple add section
        result = schedule.add_section(self.sec1_c1)
        self.assertTrue(result)  # return value
        self.assertTrue(self.sec1_c1 in schedule.sections.all())  # postcondition

    def test_add_section_prereq_success(self):
        student = Student.objects.create_user('test_add_section_prereq_success', 'test@test.com', 'testpassword')
        schedule = Schedule.objects.create(
            student=student,
            term=2)
        student.courses_taken.add(self.c1)
        # Add section that has c1 as prereq
        result = schedule.add_section(self.sec2_c2)
        self.assertTrue(result)  # return value
        self.assertTrue(self.sec2_c2 in schedule.sections.all())  # postcondition

    def test_add_section_prereq_fail(self):
        student = Student.objects.create_user('test_add_section_prereq_fail', 'test@test.com', 'testpassword')
        schedule = Schedule.objects.create(
            student=student,
            term=2)
        # Add section that has c1 as prereq
        result = schedule.add_section(self.sec2_c2)
        self.assertFalse(result)  # return value
        self.assertFalse(self.sec2_c2 in schedule.sections.all())  # postcondition

    def test_add_section_coreq_success(self):
        student = Student.objects.create_user('test_add_section_coreq_success', 'test@test.com', 'testpassword')
        schedule = Schedule.objects.create(
            student=student,
            term=2)
        schedule.courses.add(self.c1)
        # Add section that has c1 as coreq
        result = schedule.add_section(self.sec3_c3)
        self.assertTrue(result)  # return value
        self.assertTrue(self.sec3_c3 in schedule.sections.all())  # postcondition

    def test_add_section_coreq_fail(self):
        pass

    def test_remove_section_typical(self):
        pass

    def test_remove_section_coreq(self):
        pass