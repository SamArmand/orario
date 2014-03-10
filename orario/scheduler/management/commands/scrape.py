# -*- coding: utf-8 -*-
import re
import datetime
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand, CommandError
from scheduler.models import *


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

        # Regex to match various things, thank you George for your regex skillz
        terms = re.compile(r'^[(&nbsp;)\W]*/[1-4]$')
        for anchor in course_anchors:
            course = Course()
            course_number = anchor.next_sibling
            course_title = course_number.next_sibling
            course_credits = course_title.next_sibling

            course.number = course_number.text
            course.title = course_title.text
            course.credits = course_credits.text
            course.save()

            section = Section()  # Stub Section to create Section objects as we iterate through the rows.
            section.course = course

            #iterate through all rows
            for row in anchor.parent.next_siblings:
                try:
                    # Next course, so break from loop
                    if row('td', style='background-color:Maroon;'):
                        break
                    # Row is a prereq list
                    elif 'Prerequisite:' in row.contents[2].text:
                        handle_prereqs(row)
                    # Row is a special note
                    elif 'Special Note' in row.contents[2].text:
                        handle_note(row)
                    # Row contains section info
                    elif terms.match(row.contents[2].text) is not None:
                        handle_section(section, row)
                        print section
                except IndexError:
                    pass
                except AttributeError:
                    pass
                except TypeError:
                    pass


def handle_prereqs(row):
    """ Returns a dict of prereqs in the form
        of course numbers . Format:

        {
            'prereqs': ('COMP 232', ...),
            'coreqs': ('SOEN 331', ...),
            'other': 'notes, etc'
        }

        @author Felicis pls
    """
    pass
    # print row.contents[3].text


def handle_note(row):
    """ Returns a string containing the special
        note.
    """
    pass


def handle_section(section, row):
    """ Handles adding table row into the database as
        a new SectionSlot and either updates given section
        or duplicates it with new information.
    """
    times = to_time(row.contents[4].text.split()[1])
    sect_dict = {
        'term': row.contents[2].text[-1],
        'type': row.contents[3].text.split()[0],
        'section_code': row.contents[3].text.split()[1],
        'days': to_binary(row.contents[4].text.split()[0]),
        'begin_time': times[0], 'end_time': times[1],
        'room': row.contents[5].text.strip(),
        'instructor': row.contents[6].text.strip()
    }

    if sect_dict['type'] == 'Lect':
        # We always create a new Section for a new LectureSlot.
        lect = LectureSlot(sect_dict)
        lect.save()
        section.lecture = lect
        section.save()
    elif sect_dict['type'] == 'Tut':
        # If the current Section has no Tutorial nor Lab, then
        # it is incomplete, so we add the Tutorial in and
        # save it. If it does have a Tutorial, then it is
        # another distinct Section so we duplicate it with
        # the new Tutorial. We also clear its Lab to allow for
        # new Lab sections to be added.
        tut = TutorialSlot(sect_dict)
        tut.save()
        if (section.tutorial is None) and (section.lab is None):
            section.tutorial = tut
            section.save()
        elif section.tutorial is not None:
            section.pk = None
            section.lab = None
            section.tutorial = tut
            section.save()
        else:
            raise Exception('Tutorial section encountered beneath Lab section')
    elif sect_dict['type'] == 'Lab':
        # If the current Section has no lab, then we add it and
        # save it. Otherwise, we duplicate it with the new lab.
        lab = TutorialSlot(sect_dict)
        lab.save()
        if section.lab is None:
            section.lab = lab
            section.save()
        else:
            section.pk = None
            section.lab = lab
            section.save()


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
    values = re.split(r'\(\):\-', str_times)[1:4]  # Because fuck you
    ret.append(datetime.time(int(values[0]), int(values[1])))
    ret.append(datetime.time(int(values[2]), int(values[3])))
    return ret