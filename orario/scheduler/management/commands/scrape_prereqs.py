# -*- coding: utf-8 -*-
import re
import datetime

from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist

from course_calendar.models import *
from scheduler.models import *

from prereqs import get_prereq_dict

class Command(BaseCommand):
    args = '<html file to scrape>'
    help = 'Scrapes the specified HTML file to import its contents into the database. At the moment,' \
           'does not check for duplicates.'

    def handle(self, *args, **options):
        try:
            soup = BeautifulSoup(open(args[0]))
        except IOError, e:
            print e
            soup = None
            exit()

        master = soup.find(id='ctl00_PageBody_tblBodyShow1')
        course_anchors = master('td', style='background-color:Maroon;')

        # Second pass to assign prereqs and coreqs
        for anchor in course_anchors:
            course_number = anchor.next_sibling.text

            course = Course.objects.get(number=course_number)
            for row in anchor.parent.next_siblings:
                try:
                    # Next course, so break from loop
                    if row('td', style='background-color:Maroon;'):
                        break
                    # Row is a prereq list
                    elif 'Prerequisite:' in row.contents[2].text:
                        self.handle_prereqs(course, row)
                except IndexError, e:
                    self.stdout.write(e.__unicode__())
                except AttributeError, e:
                    self.stdout.write(e.__unicode__())


    def handle_prereqs(self, course, row):
        """ Returns a dict of prereqs in the form
            of course numbers . Format:

            {
                'prereqs': ('COMP 232', ...),
                'coreqs': ('SOEN 331', ...),
                'other': 'notes, etc'
            }

            @author Felicis pls
        """
        formatted = " ".join(row.contents[3].text.strip().split())
        requisites = get_prereq_dict(formatted)
        print course
        print formatted
        print repr(requisites)
        for prereq in requisites['prereqs']:
            try:
                prereq_ob = Course.objects.get(number=prereq)
                course.prereqs.add(prereq_ob)
            except ObjectDoesNotExist:
                pass

        for coreq in requisites['coreqs']:
            try:
                coreq_ob = Course.objects.get(number=coreq)
                course.coreqs.add(coreq_ob)
            except ObjectDoesNotExist:
                pass


def to_binary(str_days):
    b_days = 0
    day = 1
    for char in str_days:
        if char != "-":
            b_days |= day
        day <<= 1
    return b_days


def to_time(str_times):
    # (08:45-10:45)
    ret = []
    values = [int(s) for s in re.findall(r'\d+', str_times)]
    ret.append(datetime.time(int(values[0]), int(values[1])))
    ret.append(datetime.time(int(values[2]), int(values[3])))
    return ret