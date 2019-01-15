# Imports
from icalendar import Calendar, Event, vText, vDatetime,vRecur
from datetime import datetime, timedelta
import tempfile, os

# Read file 
def read_file ():
    path = "source.txt"
    file = open(path,'r')
    source = file.readlines()
    file.close() 
    return source

# Seperate each course
def seperate_course(source):
    courses = []
    course = []
    is_begin = False
    begin_indicator = 'Status\tUnits\tGrading\tDeadlines\n'
    end_indicator = 'Printer Friendly Page\n'
    for index, line in enumerate(source):
        if( line == end_indicator):
            courses.append(course)
            is_begin = False      
            return courses
        elif(line == begin_indicator):
            if (is_begin):
                course.pop()
                course.pop()
                courses.append(course)
                course = []
            is_begin = True            
            course.append(source[index-2])
        elif(is_begin):
            course.append(line)
        else:
            continue
            
#     error handling 
    if (not len(courses)):
        print('has nothing')

def parseTime (time):
    # reformat from 12 hour display to 24 hour display
    a_or_p = True if (time[-2:] == 'PM' and int(time[0:-5]) <12) else False
    hour = int(time[0:-5]) + 12 if (a_or_p ) else  int(time[0:-5])
    minute = int(time[-4:-2])
    return hour, minute

def parseWeek(week):
    a = []
    for index, day in enumerate(week):

        if(day == 'M' or day == 'm'):
            a.append( 'MO')
        elif(day == 'W' or day == 'w'):
            a.append( 'WE')
        elif(day == 'F' or day == 'f'):
            a.append( 'FR')
        elif((day == 'T' or day == 't') and (index+1) >= len(week)):
            a.append( 'TU')
        elif((day == 'T' or day == 't') and (week[index+1] != 'h')):
            a.append( 'TU')
        elif((day == 'T' or day == 't') and (week[index+1] == 'h')):
            a.append( 'TH')
    return a


def seperate_lec(source, UID, cal):
    count = 1;
    for course in source:
        if (course[1] == 'Dropped\n'):
            continue
        for x in range (6, len(course), 7):
            event = Event()
            if(course[x] != ' \n'):
                name = course[0].replace("\n", "")
                section = course[x+1].replace("\n", "")
                component = course[x+2].replace("\n", "")  
            # Get date
            dates = course[x+6].replace("\n", "").split(' ')
            if (dates[0] == 'TBA'):
                continue;
            start_dates = dates[0].split('/')
            end_dates = dates[2].split('/')
    
            # Get time
            time = course[x+3].replace("\n", "").split(' ')
            start_hour, start_minute = parseTime(time[1])
            end_hour, end_minute = parseTime(time[3])
            
            # Reccurance
            week = parseWeek(time[0])
            until = datetime(int(end_dates[2]), int(end_dates[1]), int(end_dates[0]), end_hour, end_minute)
            rec = {
                'FREQ': 'WEEKLY',
                'INTERVAL': 1,
                'BYDAY': week,
                'UNTIL': until,
                'WKST': 'SU',
            }
            
            week_dic = {
                'MO': 0,
                'TU': 1,
                'WE': 2,
                'TH': 3,
                'FR': 4
            }
            
            # Prepare information 
            summary =  name + ' (' + component + ')'
            uid = UID + '_' + str(count)
            location = course[x+4].replace("\n", "") + ', Waterloo, Canada'
            instructor = course[x+5].replace("\n", "")
            description = ('Course name: %s %s (%s)\nLocation: %s\nInstructor: %s' ) % (name, component, section, location, instructor )
            
            
            # Prepare Date
            dtstart = datetime(int(start_dates[2]), int(start_dates[1]), int(start_dates[0]), start_hour, start_minute, )
            dtend = datetime(int(start_dates[2]), int(start_dates[1]), int(start_dates[0]), end_hour, end_minute)
#             print(dtstart.weekday() - week_dic[week[0]])
            diff = week_dic[week[0]] - dtstart.weekday()
            
            dtstart += timedelta(days=diff)
            dtend += timedelta(days=diff)
            
            
            
            event['summary'] = vText(summary)
            event['uid'] = vText(uid)
            event['dtstamp'] = vDatetime(datetime.now())
            event['location'] = vText(location)
            event['description'] = vText(description)
            event['dtstart'] = vDatetime(dtstart)
            event['dtend'] = vDatetime(dtend)
            event['rrule']= vRecur(rec)
            
            cal.add_component(event)
            count += 1

'''
1. read source............................(check)
2. seperate each course...................(check)
3. seperate each course component and lec.(check)
4. generate the class 
5. write file
'''

# Read file/input
source = read_file()
# print(source)
# Seperate course
courses = seperate_course(source)

# Get Indentifier
term = source[20].split(' ')[0:2]
name = source[6].replace('\n', '').replace(' ', '_')
UID = ( name + '_' + term[0] + '_' + term[1])

# Create the calender class
cal = Calendar()
cal.add('version', '2.0')
cal.add('prodid', UID)

# Seperate lecture and create each event 
seperate_lec(courses, UID, cal)
# print (display(cal))

# Write file 
f = open(os.path.join('test.ics'), 'wb')
f.write(cal.to_ical())
f.close()
# print('successfully writing the file')
# try:

# except:
#     print('experience an error when writting the file')


    