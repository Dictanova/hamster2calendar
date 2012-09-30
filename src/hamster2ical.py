#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Convert time tracking done by hamster for a particular periode of time passed in
parameter into an iCal file.
"""

import sys, socket, json
# Hamster API
import hamster.client
# iCal API
from icalendar import Calendar, Event
import pytz
from datetime import datetime

if __name__ == "__main__":
	# Check configuration
	if len(sys.argv) < 3:
		print "Usage:"
		print "\t%s <backup path> <start date dd/mm/yyyy> [<end date dd/mm/yyyy>]" % sys.argv[0]
		sys.exit(1)
	filepath = sys.argv[1]
	start = datetime.strptime(sys.argv[2], "%d/%m/%Y")
	if len(sys.argv) > 3:
		end = datetime.strptime(sys.argv[3], "%d/%m/%Y")
	else:
		end = datetime.today()
	# Prepare calendar
	cal = Calendar()
	cal.add('prodid', '-//Hamster backup//')
	cal.add('version', '2.0')
	# Extract facts as calendar events
	storage = hamster.client.Storage()
	for fact in storage.get_facts(start, end_date=end):
		event = Event()
		event["uid"] = "%s@%s" % (fact.id, socket.gethostname())
		event.add("x-hamster-activityid", u"%s"%fact.activity_id)
		event.add("x-hamster-category", u"%s"%fact.category)
		event.add("x-hamster-tags", json.dumps([u"%s"%tag for tag in fact.tags]))
		event.add("partstat", "accepted")
		event.add("role", "chair")
		event.add("summary", fact.activity)
		description  = u"%s@%s\\n" % (fact.activity, fact.category)
		description += u" ".join(fact.tags) + "\\n"
		if (not fact.description is None) and (len(fact.description) > 0):
			description += fact.description.replace("\n", "\\n")
		event.add("description", description)
		dtstart = datetime(fact.start_time.year, fact.start_time.month, 
			fact.start_time.day, fact.start_time.hour, fact.start_time.minute,
			tzinfo=pytz.timezone("Europe/Paris"))
		event.add('dtstart', dtstart)
		if not fact.end_time is None:
			dtend = datetime(fact.end_time.year, fact.end_time.month, 
				fact.end_time.day, fact.end_time.hour, fact.end_time.minute,
				tzinfo=pytz.timezone("Europe/Paris"))
			event.add('dtend', dtend)
		else:
			print "Error: unclosed activity started on %s" % fact.start_time
		cal.add_component(event)
	# Export
	f = open(filepath, 'wb')
	f.write(cal.to_ical())
	f.close()

