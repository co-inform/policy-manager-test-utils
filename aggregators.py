import json
import os
from pathlib import Path
import argparse
import array as arr
import csv

import numpy as np
import pandas as pd


'''
module name: e.g misinfome
result: cred, confidence values, label
get all values and take average, then set it to final label
'''








CRED_WEIGHTS = [['misinfome',1], ['content_analys',4], ['claim',3]]



def maximum(credibility_results, thresholds):

    outputs = []

    misinfome_conf = credibility_results["misinfome"]["conf"]
    content_analys_conf = credibility_results["stance"]["conf"]
    claim_conf = credibility_results["claim_credibility"]["conf"]

    misinfome_cred = credibility_results["misinfome"]["cred"]
    content_analys_cred = credibility_results["stance"]["cred"]
    claim_cred = credibility_results["claim_credibility"]["cred"]

    maximum_confidence = np.maximum(np.maximum(misinfome_conf, content_analys_conf), claim_conf)
    maximum_credibility = np.maximum(np.maximum(misinfome_cred, claim_cred), content_analys_cred)

    if maximum_confidence < 0.5:
        outputs.append('not_verifiable')
    elif maximum_confidence >= 0.5:
        for label, threshold in thresholds:
            if maximum_credibility >= threshold:
                outputs.append(label)
                break
    for item in outputs:
        return item






def default(credibility_results, thresholds):

    outputs = []

    misinfome_cred = credibility_results["misinfome"]["cred"]
    content_analys_cred = credibility_results["stance"]["cred"]
    claim_cred = credibility_results["claim_credibility"]["cred"]

    for label, threshold in thresholds:
                if (misinfome_cred > threshold) & (content_analys_cred > threshold):
                    outputs.append(label)
                elif (misinfome_cred > threshold) & (claim_cred > threshold):
                    outputs.append(label)
                elif (content_analys_cred > threshold) & (claim_cred > threshold):
                    outputs.append(label)
                else:
                    outputs.append('not_verifiable')
                    break
    for item in outputs:
        print(item)
        return item


def dummy_output(credibility_results):
    labels = ['credible', 'mostly_credible', 'mostly_not_credible', 'credible_uncertain', 'not_credible',
              'not_verifiable']
    random_idx = np.random.randint(high=len(labels), low=0, size=1)[0]
    return labels[random_idx]



def weighted_average(credibility_results, thresholds):

    outputs = []

    misinfome_conf = credibility_results["misinfome"]["conf"]
    content_analys_conf = credibility_results["stance"]["conf"]
    claim_conf = credibility_results["claim_credibility"]["conf"]

    misinfome_cred = credibility_results["misinfome"]["cred"]
    content_analys_cred = credibility_results["stance"]["cred"]
    claim_cred = credibility_results["claim_credibility"]["cred"]



    weighted_average_credibility = (misinfome_cred * CRED_WEIGHTS[0][1] +
                                        claim_cred * CRED_WEIGHTS[1][1] +
                                        content_analys_cred * CRED_WEIGHTS[2][1]) / (
                                                   CRED_WEIGHTS[0][1] + CRED_WEIGHTS[1][1] + CRED_WEIGHTS[2][1])

    weighted_average_confidence = (misinfome_conf * CRED_WEIGHTS[0][1] +
                                        claim_conf * CRED_WEIGHTS[1][1] +
                                        content_analys_conf * CRED_WEIGHTS[2][1]) / (
                                                   CRED_WEIGHTS[0][1] + CRED_WEIGHTS[1][1] + CRED_WEIGHTS[2][1])



    if weighted_average_confidence < 0.5:
        outputs.append('not_verifiable')
    else:
        for label, threshold in thresholds:
            if weighted_average_credibility >= threshold:
                outputs.append(label)
                break
    for item in outputs:
        return item




methods = {

    'default': default,
    'dummy_output': dummy_output,
    'weighted_average': weighted_average,
    'maximum': maximum

}
