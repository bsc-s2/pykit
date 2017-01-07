
import dictutil

records = [
    {"event": 'log in',
     "time": {"hour": 10, "minute": 30, }, },

    {"event": 'post a blog',
     "time": {"hour": 10, "minute": 40, }, },

    {"time": {"hour": 11, "minute": 20, }, },

    {"event": 'log out',
     "time": {"hour": 11, "minute": 20, }, },
]

get_event = dictutil.make_getter('event', default="NOTHING DONE")
get_time = dictutil.make_getter('time.$field')

for record in records:

    ev = get_event(record)

    tm = "%d:%d" % (get_time(record, {"field": "hour"}),
                    get_time(record, {"field": "minute"}))

    print "{ev:<12}   at {tm}".format(ev=ev, tm=tm)

# output:
# log in         at 10:30
# post a blog    at 10:40
# NOTHING DONE   at 11:20
# log out        at 11:20
