# -*- coding:utf-8 -*-
import re

disciplines = ['BLDG', 'MATH', 'BCEE', 'ENGR', 'ENCS', 'CHEM', 'COEN', 'CIVI', 'ELEC', 'COMP', 'PHYS', 'MECH', 'INDU',
               'SOEN', 'CEGEP MATHEMATICS']
creditDisciplines = ['COMPUTER', 'BULDING', 'CIVIL', 'ELECTRICAL', 'COMP.SC']

# Damn you Felicia...
#
# def get_prereq_dict(line):
#     ret = {'prereqs': [], 'coreqs': [], 'notes': []}
#     validLine = re.sub(r'[\xc2\x99]', " ", line).upper()
#     if validLine.find('CONCURRENTLY') > -1:
#         for discipline in disciplines:
#             foundDiscipline = validLine.find(discipline)
#             if foundDiscipline > -1:
#                 if discipline == 'CEGEP MATHEMATICS':
#                     ret['coreqs'].append(validLine[foundDiscipline:foundDiscipline + 21])
#                 ret['coreqs'].append(validLine[foundDiscipline:foundDiscipline + 8])
#     else:  # prerequisites found.
#         foundCredits = validLine.find('CREDITS')
#         if foundCredits > -1:
#             # print('CREDITS FOUNDS*******')
#             for creditDiscipline in creditDisciplines:
#                 foundCreditDiscipline = validLine.find(creditDiscipline)
#                 if foundCreditDiscipline > -1:
#                     # print('FOUND EVEN MORE!!!')
#                     # print(creditDiscipline)
#                     # print(validLine[foundCredits:foundCreditDiscipline])
#                     lengthOfDisci = len(creditDiscipline)
#                     ret['prereqs'].append(validLine[foundCredits - 3:foundCreditDiscipline + lengthOfDisci + 1])
#         for discipline in disciplines:
#             foundDiscipline = validLine.find(discipline)
#             if foundDiscipline > -1:
#                 ret['prereqs'].append(validLine[foundDiscipline:foundDiscipline + 8])
#     return ret

def get_prereq_dict(line):
    ret = {'prereqs': [], 'coreqs': [], 'notes': []}
    parts = line.split("; ")
    course_pattern = re.compile(r'[A-Z]{4} [0-9]{3}')
    coreq_pattern = re.compile(r'concurrently')
    for part in parts:
        if coreq_pattern.findall(part):
            for coreq in course_pattern.findall(part):
                ret['coreqs'].append(coreq)
        else:
            for prereq in course_pattern.findall(part):
                ret['prereqs'].append(prereq)
    return ret


def main(*args, **kwargs):
    file = open('prereqs.out', 'r')
    for line in file:
        print repr(get_prereq_dict(line))

    file.close()


if __name__ == "__main__":
    main()