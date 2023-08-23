#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import random
import os


TPS_DIR = '../Data'

col_names = ["item_id", "user_id", "ratings", "ts"]
df = pd.read_csv('../Data/item_user.csv', names=col_names)

item_user_rating = {}

i=0
for index, row in df.iterrows():
    i = i + 1
    print i
    if row['item_id'] not in item_user_rating:
        item_user_rating[row['item_id']] = range(20283)
    if row['user_id'] in item_user_rating[row['item_id']]:
        item_user_rating[row['item_id']].remove(row['user_id'])


item_user_test_pos = {}

test_item = []
test_user = []
test_ratings = []
test_ts = []

test_neg_iu = []
test_neg_samples = []

train_item = []
train_user = []
train_ratings = []
train_ts = []


col_names = ["item_id", "user_id", "ratings", "ts"]
df = pd.read_csv('../Data/item_user.csv', names=col_names)
for index, row in df.iterrows():
    if row['ratings'] == 1:
        if row['item_id'] not in item_user_test_pos:
            item_user_test_pos[row['item_id']] = 1
            test_item.append(row['item_id'])
            test_user.append(row['user_id'])
            test_ratings.append(row['ratings'])
            test_ts.append(row['ts'])

            iu = '(' + str(row['item_id']) + ',' + str(row['user_id']) + ')'
            test_neg_iu.append(iu)

            rs = random.sample(item_user_rating[row['item_id']], 99)
            test_neg_samples.append("\t".join(map(str, rs)))

        else:
            train_item.append(row['item_id'])
            train_user.append(row['user_id'])
            train_ratings.append(row['ratings'])
            train_ts.append(row['ts'])

train_df = pd.DataFrame({'item_id': pd.Series(train_item),
                         'user_id': pd.Series(train_user),
                         'ratings': pd.Series(train_ratings),
                         'ts': pd.Series(train_ts)})[['item_id', 'user_id', 'ratings', 'ts']]

train_df.to_csv(os.path.join(TPS_DIR, 'kariyer.train.rating'), index=False,header=None, sep='\t')

test_df = pd.DataFrame({'item_id': pd.Series(test_item),
                        'user_id': pd.Series(test_user),
                        'ratings': pd.Series(test_ratings),
                        'ts': pd.Series(test_ts)})[['item_id', 'user_id', 'ratings', 'ts']]

test_df.to_csv(os.path.join(TPS_DIR, 'kariyer.test.rating'), index=False,header=None, sep='\t')


test_negative_df = pd.DataFrame({'neg_ui': pd.Series(test_neg_iu),
                                 'neg_samples': pd.Series(test_neg_samples)})[['neg_ui', 'neg_samples']]

test_negative_df.to_csv(os.path.join(TPS_DIR, 'kariyer.test.negative'), index=False,header=None, sep='\t')
