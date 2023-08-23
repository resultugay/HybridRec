#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import random
import os


TPS_DIR = '../Data'

col_names=["user_id", "item_id", "ratings", "ts"]
df = pd.read_csv('../Data/user_item.csv', names=col_names)

user_item_rating = {}

i=0
for index, row in df.iterrows():
    i = i + 1
    print i
    if row['user_id'] not in user_item_rating:
        user_item_rating[row['user_id']] = range(16134)
    if row['item_id'] in user_item_rating[row['user_id']]:
        user_item_rating[row['user_id']].remove(row['item_id'])


user_item_test_pos = {}

test_user = []
test_item = []
test_ratings = []
test_ts = []

test_neg_ui = []
test_neg_samples = []

train_user = []
train_item = []
train_ratings = []
train_ts = []


col_names = ["user_id", "item_id", "ratings", "ts"]
df = pd.read_csv('../Data/user_item.csv', names=col_names)
for index, row in df.iterrows():
    if row['ratings'] == 1:
        if row['user_id'] not in user_item_test_pos:
            user_item_test_pos[row['user_id']] = 1
            test_user.append(row['user_id'])
            test_item.append(row['item_id'])
            test_ratings.append(row['ratings'])
            test_ts.append(row['ts'])

            ui = '(' + str(row['user_id']) + ',' + str(row['item_id']) + ')'
            test_neg_ui.append(ui)

            rs = random.sample(user_item_rating[row['user_id']], 99)
            test_neg_samples.append("\t".join(map(str, rs)))

        else:
            train_user.append(row['user_id'])
            train_item.append(row['item_id'])
            train_ratings.append(row['ratings'])
            train_ts.append(row['ts'])

train_df = pd.DataFrame({'user_id': pd.Series(train_user),
                         'item_id': pd.Series(train_item),
                         'ratings': pd.Series(train_ratings),
                         'ts': pd.Series(train_ts)})[['user_id', 'item_id', 'ratings', 'ts']]

train_df.to_csv(os.path.join(TPS_DIR, 'kariyer.train.rating'), index=False,header=None, sep='\t')

test_df = pd.DataFrame({'user_id': pd.Series(test_user),
                        'item_id': pd.Series(test_item),
                        'ratings': pd.Series(test_ratings),
                        'ts': pd.Series(test_ts)})[['user_id', 'item_id', 'ratings', 'ts']]

test_df.to_csv(os.path.join(TPS_DIR, 'kariyer.test.rating'), index=False,header=None, sep='\t')


test_negative_df = pd.DataFrame({'neg_ui': pd.Series(test_neg_ui),
                                 'neg_samples': pd.Series(test_neg_samples)})[['neg_ui', 'neg_samples']]

test_negative_df.to_csv(os.path.join(TPS_DIR, 'kariyer.test.negative'), index=False,header=None, sep='\t')
