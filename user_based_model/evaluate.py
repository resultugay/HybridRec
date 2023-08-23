'''
Created on Apr 15, 2016
Evaluate the performance of Top-K recommendation:
    Protocol: leave-1-out evaluation
    Measures: Hit Ratio and NDCG
    (more details are in: Xiangnan He, et al. Fast Matrix Factorization for Online Recommendation with Implicit Feedback. SIGIR'16)
@author: hexiangnan
'''
import math
import heapq  # for retrieval topK
import multiprocessing
import numpy as np
from time import time
import csv # write recommendation result to a csv file named "rec_results.csv"

# from numba import jit, autojit

# Global variables that are shared across processes
_model = None
_testRatings = None
_testNegatives = None
_K = None


def evaluate_model(model, testRatings, testNegatives, K, num_thread,last_iteration):
    """
    Evaluate the performance (Hit_Ratio, NDCG) of top-K recommendation
    Return: score of each test rating.
    """
    global _model
    global _testRatings
    global _testNegatives
    global _K
    _model = model
    _testRatings = testRatings
    _testNegatives = testNegatives
    _K = K

    hits, ndcgs = [], []
    if (num_thread > 1):  # Multi-thread
        pool = multiprocessing.Pool(processes=num_thread)
        res = pool.map(eval_one_rating, range(len(_testRatings)),last_iteration)
        pool.close()
        pool.join()
        hits = [r[0] for r in res]
        ndcgs = [r[1] for r in res]
        return (hits, ndcgs)
    # Single thread
    for idx in xrange(len(_testRatings)):
        (hr, ndcg) = eval_one_rating(idx,last_iteration)
	hits.append(hr)
        ndcgs.append(ndcg)
    return (hits, ndcgs)


def eval_one_rating(idx,last_iteration):
    rating = _testRatings[idx]
    items = _testNegatives[idx]
    u = rating[0]
    gtItem = rating[1]
    items.append(gtItem)
    # Get prediction scores
    map_item_score = {}
    users = np.full(len(items), u, dtype='int32')
    predictions = _model.predict([users, np.array(items)],
                                 batch_size=100, verbose=0)
    for i in xrange(len(items)):
        item = items[i]
        map_item_score[item] = predictions[i]
    items.pop()

    if last_iteration:  # This writes at the last iteration
    	with open('rec_results.csv', mode='a') as rec_results_file: # This opens and closes automatically csv file.
	   rec_results = csv.writer(rec_results_file, delimiter=',')
	   tmp_list = []
	   tmp_list.append(u)	
           for key,val in map_item_score.items():
	      tmp_list.append(key)
	   rec_results.writerow(tmp_list)

    # Evaluate top rank list
    ranklist = heapq.nlargest(_K, map_item_score, key=map_item_score.get)
    hr = getHitRatio(ranklist, gtItem)
    ndcg = getNDCG(ranklist, gtItem)
    return (hr, ndcg)


def getHitRatio(ranklist, gtItem):
    for item in ranklist:
        if item == gtItem:
            return 1
    return 0


def getNDCG(ranklist, gtItem):
    for i in xrange(len(ranklist)):
        item = ranklist[i]
        if item == gtItem:
            return math.log(2) / math.log(i + 2)
    return 0
