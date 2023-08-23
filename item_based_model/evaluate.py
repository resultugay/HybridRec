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

# from numba import jit, autojit

# Global variables that are shared across processes
_model = None
_testRatings = None
_testNegatives = None
_K = None


def evaluate_model(model, testRatings, testNegatives, K, num_thread):
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
        res = pool.map(eval_one_rating, range(len(_testRatings)))
        pool.close()
        pool.join()
        hits = [r[0] for r in res]
        ndcgs = [r[1] for r in res]
        return (hits, ndcgs)
    # Single thread
    for idx in xrange(len(_testRatings)):
        (hr, ndcg) = eval_one_rating(idx)
        hits.append(hr)
        ndcgs.append(ndcg)
    return (hits, ndcgs)


def eval_one_rating(idx):
    rating = _testRatings[idx]
    users = _testNegatives[idx]
    u = rating[0]
    gtUser = rating[1]
    users.append(gtUser)
    # Get prediction scores
    map_user_score = {}
    items = np.full(len(users), u, dtype='int32')
    predictions = _model.predict([items, np.array(users)],
                                 batch_size=100, verbose=0)
    for i in xrange(len(users)):
        user = users[i]
        map_user_score[user] = predictions[i]
    users.pop()

    # Evaluate top rank list
    ranklist = heapq.nlargest(_K, map_user_score, key=map_user_score.get)
    hr = getHitRatio(ranklist, gtUser)
    ndcg = getNDCG(ranklist, gtUser)
    return (hr, ndcg)


def getHitRatio(ranklist, gtUser):
    for user in ranklist:
        if user == gtUser:
            return 1
    return 0


def getNDCG(ranklist, gtUser):
    for i in xrange(len(ranklist)):
        user = ranklist[i]
        if user == gtUser:
            return math.log(2) / math.log(i + 2)
    return 0
