# -*- coding: utf-8 -*-
import re
import datetime
from bs4 import BeautifulSoup

import sys
import codecs
sys.stdout = codecs.getwriter('utf8')(sys.stdout)
reload(sys)
sys.setdefaultencoding('utf-8')

def main():
    soup = BeautifulSoup(open('fw2013.html'))
    master = soup.find(id='ctl00_PageBody_tblBodyShow1')
    course_anchors = master('td', style='background-color:Maroon;')

    # Regex to match various things, thank you George for your regex skillz
    terms = re.compile(r'^[(&nbsp;)\W]*\/[1-4]$')
    for anchor in course_anchors:
        course_number = anchor.next_sibling
        course_title = course_number.next_sibling
        course_credits = course_title.next_sibling
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
                    handle_section(row)
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

def handle_section(row):
    """ Returns a dict containing all the attributes
        of the section.

        {
            'term': 2,  # or 1, or 4
            'type': 'Lect',  # or 'Tut', 'Lab'
            'section_code': 'AA',  # Letter code
            'days': 0b0001010,  # Tuesday and Thursday
            'begin_time': time('22:00'),  # datetime.time object
            'end_time': time('23:15'),
            'room': 'SGW H420',
            'instructor': 'Master Yi',
        }
    """

    # Cell 0: \n
    # Cell 1: <td colspan="1"> </td>
    # Cell 2: <td colspan="1" style="font-size:8pt;">    /3</td>
    # Cell 3: <td align="left" colspan="1" style="font-size:10pt;font-weight:normal;white-space:nowrap;">   <b>Lab</b> <b>SJ</b></td>
    # Cell 4: <td align="left" colspan="1" style="font-size:10pt;font-weight:normal;white-space:nowrap;">-T-J--- (08:45-10:45) </td>
    # Cell 5: <td align="left" colspan="1" style="font-size:10pt;font-weight:normal;white-space:nowrap;">SGW H-825       </td>
    # Cell 6: <td align="left" colspan="1" style="font-size:10pt;font-weight:bold;white-space:nowrap;"> </td>
    # Cell 7: \n

    ret = {}
    ret['term'] = row.contents[2].text[-1]
    ret['type'] = row.contents[3].text.split()[0]
    ret['section_code'] = row.contents[3].text.split()[1]
    ret['days'] = to_binary(row.contents[4].text.split()[0])
    times = to_time(row.contents[4].text.split()[1])
    ret['begin_time'] = times[0]
    ret['end_time'] = times[1]
    ret['room'] = row.contents[5].text.strip()
    ret['instructor'] = row.contents[6].text.strip()

    print ret
    return ret


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
    values = re.split(r"\(\)\:\-", str_times)[1:4]  # Because fuck you
    ret.append(datetime.time(int(values[0]), int(values[1])))
    ret.append(datetime.time(int(values[2]), int(values[3])))

    
if __name__ == '__main__':
    main()