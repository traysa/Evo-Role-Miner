__author__ = 'Theresa'

import datetime

a = datetime.datetime.now()
b = datetime.datetime.now()
c = b - a
c = datetime.timedelta(0, 4, 316543)
print(c)
datetime.timedelta(0, 4, 316543)
print(c.days)
print(c.seconds)
print(c.microseconds)
