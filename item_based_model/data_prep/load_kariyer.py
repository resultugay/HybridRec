#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unicodecsv
import pandas as pd
import os
import datetime as dt

TPS_DIR = '../Data'


# CSV File Options
def unicode_csv_reader(csv_file):
    for row in csv_file:
        yield [cell.encode("utf-8") for cell in row]


def read_csv_file(file):
    csv_file = unicodecsv.reader(file, encoding='latin5')
    # skip first line
    next(csv_file)

    file = unicode_csv_reader(csv_file)
    return file


def str_to_int(value):
    if value == "":
        return 0
    return int(value)


# APPLICATION PART
application = open('../../../data/applications.csv', 'r')
application_data = read_csv_file(application)

i = 0
aday_id = []
ilan_id = []
ratings = []
ts = []

for row in application_data:
    i = i + 1
    print i

    values = map((lambda x: ''+x+''), row)

    aday_id.append(str_to_int(values[2]))
    ilan_id.append(str_to_int(values[1]))
    ratings.append(1)
    date = dt.datetime.strptime(values[4], '%Y-%m-%d %H:%M')
    t = timestamp = (date - dt.datetime(1970, 1, 1)).total_seconds()
    ts.append(int(t))

application.close()


# JOBVIEW PART
job_views = open('../../../data/jobviews.csv', 'r')
jobview_data = read_csv_file(job_views)

for row in jobview_data:
    i = i + 1
    print i

    values = map((lambda x: ''+x+''), row)

    aday_id.append(str_to_int(values[1]))
    ilan_id.append(str_to_int(values[0]))
    ratings.append(0)
    date = dt.datetime.strptime(values[2], '%Y-%m-%d %H:%M:%S')
    t = timestamp = (date - dt.datetime(1970, 1, 1)).total_seconds()
    ts.append(int(t))

job_views.close()


data = pd.DataFrame({'item_id': pd.Series(ilan_id),
                     'user_id': pd.Series(aday_id),
                     'ratings': pd.Series(ratings),
                     'ts': pd.Series(ts)})[['item_id', 'user_id', 'ratings', 'ts']]


def get_count(tp, id):
    playcount_groupbyid = tp[[id, 'ratings']].groupby(id, as_index=False)
    count = playcount_groupbyid.size()
    return count


usercount, itemcount = get_count(data, 'user_id'), get_count(data, 'item_id')
unique_uid = usercount.index
unique_sid = itemcount.index
print len(unique_uid), len(unique_sid)
item2id = dict((sid, i) for (i, sid) in enumerate(unique_sid))
user2id = dict((uid, i) for (i, uid) in enumerate(unique_uid))


def numerize(tp):
    uid = map(lambda x: user2id[x], tp['user_id'])
    sid = map(lambda x: item2id[x], tp['item_id'])
    tp['user_id'] = uid
    tp['item_id'] = sid
    return tp


data = numerize(data)

# Let
numeric = ['item_id', 'user_id', 'ratings', 'ts']
data[numeric] = data[numeric].apply(pd.to_numeric, errors='coerce')

sortedbyid = data.sort_values(['item_id', 'ts'], ascending=[True, False])

sortedbyid.to_csv(os.path.join(TPS_DIR, 'item_user.csv'), index=False,header=None)


