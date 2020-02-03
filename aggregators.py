import json
import os
from pathlib import Path
import argparse
import array as arr
import csv

import numpy as np
import pandas as pd
import heapq

# this is default method
from scipy.sparse import data

'''
module name: e.g misinfome
result: cred, confidence values, label
get all values and take average, then set it to final label
'''

DATA_DIR = Path(os.path.dirname(os.path.dirname(__file__))) / Path(os.path.basename(os.path.dirname(__file__))) / 'data'
for file_name in DATA_DIR.glob('*.csv'):
    results = {}
    name = file_name.name[:-4]
    results['collection'] = name
    dummy_values = pd.read_csv(file_name)
    claim_conf = dummy_values['claim_conf'].astype(float).values.tolist()
    claim_cred = dummy_values['claim_cred'].astype(float).values.tolist()
    misinfome_conf = dummy_values['misinfome_conf'].astype(float).values.tolist()
    misinfome_cred = dummy_values['misinfome_cred'].astype(float).values.tolist()
    content_analys_conf = dummy_values['content_analys_conf'].astype(float).values.tolist()
    content_analys_cred = dummy_values['content_analys_cred'].astype(float).values.tolist()



THRESHOLDS = {
    'credible': 0.6,
    'mostly_credible': 0.33,
    'credible_uncertain': -0.33,
    'mostly_not_credible': -0.66,
    'not_credible': -0.99,
}

CRED_WEIGHTS = [['misinfome',1], ['content_analys',4], ['claim',3]]



def maximum(credibility_results):

    maximum_confidence = np.maximum(np.maximum(misinfome_conf, content_analys_conf), claim_conf)

    maximum_credibility = np.maximum(np.maximum(misinfome_cred, claim_cred), content_analys_cred)



    outputs = []
    thresholds = sorted(THRESHOLDS.items(), key=lambda t: t[1], reverse=True)

    for conf in maximum_confidence:
        if conf < 0.5:
            outputs.append('not_verifiable')
        else:
            for cred in maximum_credibility:
                for label, threshold in thresholds:
                    if cred <= threshold:
                        outputs.append(label)
                        print(cred)
                        break
    for item in outputs:
        return item



def default(credibility_results):
        count =0
        outputs = []
        thresholds = sorted(THRESHOLDS.items(), key=lambda t: t[1], reverse=True)

        for label, threshold in thresholds:
            for cred1 in misinfome_cred:
                for cred2 in claim_cred:
                    if (cred1 > threshold) & (cred2 > threshold):
                        outputs.append(label)
                for cred3 in content_analys_cred:
                    if (cred1 > threshold) & (cred3 > threshold):
                        outputs.append(label)
                if (cred2 > threshold) & (cred3 > threshold):
                    outputs.append(label)
                    break
        for item in outputs:
            return item


def dummy_output(credibility_results):
    labels = ['credible', 'mostly_credible', 'mostly_not_credible', 'credible_uncertain', 'not_credible',
              'not_verifiable']
    random_idx = np.random.randint(high=len(labels), low=0, size=1)[0]
    return labels[random_idx]



def weighted_average(credibility_results):
        weighted_average_credibility = (dummy_values.misinfome_cred * CRED_WEIGHTS[0][1] +
                                        dummy_values.claim_cred * CRED_WEIGHTS[1][1] +
                                        dummy_values.content_analys_cred * CRED_WEIGHTS[2][1]) / (
                                                   CRED_WEIGHTS[0][1] + CRED_WEIGHTS[1][1] + CRED_WEIGHTS[2][1])

        weighted_average_confidence = (dummy_values.misinfome_conf * CRED_WEIGHTS[0][1] +
                                        dummy_values.claim_conf * CRED_WEIGHTS[1][1] +
                                        dummy_values.content_analys_conf * CRED_WEIGHTS[2][1]) / (
                                                   CRED_WEIGHTS[0][1] + CRED_WEIGHTS[1][1] + CRED_WEIGHTS[2][1])

        outputs = []
        thresholds = sorted(THRESHOLDS.items(), key=lambda t: t[1], reverse=True)

        for cred in weighted_average_credibility:
            for conf in weighted_average_confidence:
                if conf < 0.5:
                    outputs.append('not_verifiable')
                elif conf >= 0.5:
                    for label, threshold in thresholds:
                        if cred >= threshold:
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
