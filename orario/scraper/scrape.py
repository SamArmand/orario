# -*- coding: utf-8 -*-
import re
from bs4 import BeautifulSoup

import sys
import codecs
sys.stdout = codecs.getwriter('utf8')(sys.stdout)

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
                if 'Prerequisite:' in row.contents[2].text:
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
    """
    print row.contents[3].text
    
if __name__ == '__main__':
    main()