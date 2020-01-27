import json
import os
from pathlib import Path
import argparse

import pandas as pd
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

from aggregators import methods

'''
Pipeline for the evaluation

'''

DATA_DIR = Path(os.path.dirname(os.path.dirname(__file__))) / Path(os.path.basename(os.path.dirname(__file__))) / 'data'


def callback_aggregate(row, aggregate_func='dummy_output'):
    dummy_request = _create_request(row)
    response = methods[aggregate_func](dummy_request)
    return response


def _create_request(row):
    return {

        'misinfome': {
            'cred': row['misinfome_cred'],
            'conf': row['misinfome_conf']
        },
        'stance': {
            'cred': row['content_analys_cred'],
            'conf': row['content_analys_conf']
        },
        'claim_credibility': {
            'cred': row['claim_cred'],
            'conf': row['claim_conf']
        }

    }


def run(args):
    target_names = {'credible': 0, 'mostly_credible': 1, 'mostly_not_credible': 2, 'credible_uncertain': 3,
                    'not_credible': 4,
                    'not_verifiable': 5}
    for file_name in DATA_DIR.glob('*.csv'):
        results = {}
        name = file_name.name[:-4]
        results['collection'] = name
        dummy_values = pd.read_csv(file_name, low_memory=False)
        print(file_name)
        ground_labels = [target_names[value] for value in dummy_values.expected_credible]
        dummy_values['actual_credible'] = dummy_values.apply(lambda row: callback_aggregate(row,args.aggregate_func), axis=1)
        predictions = [target_names[value] for value in dummy_values.actual_credible]
        results['accuracy'] = accuracy_score(ground_labels, predictions)
        scores = precision_recall_fscore_support(ground_labels, predictions, average='macro',
                                                 labels=list(target_names.values()), zero_division=1)
        results['precision_macro'] = scores[0]
        results['recall_macro'] = scores[1]
        results['fscore_macro'] = scores[2]
        scores = precision_recall_fscore_support(ground_labels, predictions, average='micro',
                                                 labels=list(target_names.values()), zero_division=1)
        results['precision_micro'] = scores[0]
        results['recall_micro'] = scores[1]
        results['fscore_micro'] = scores[2]
        scores = precision_recall_fscore_support(ground_labels, predictions,
                                                 labels=list(target_names.values()), zero_division=1)
        # per class precision, recall, f1
        target_names = list(target_names.keys())
        for i, score in enumerate(scores):
            for j in range(len(target_names)):
                if i == 0:
                    column_name = 'precision_{}'.format(target_names[j])
                    results[column_name] = score[j]
                elif i == 1:
                    column_name = 'recall_{}'.format(target_names[j])
                    results[column_name] = score[j]
                elif i == 2:
                    column_name = 'fscore_{}'.format(target_names[j])
                    results[column_name] = score[j]
        name = name + '.json'
        with open(DATA_DIR / name, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--aggregate_func', type=str, default='default',
                        help="Select aggregate function e.g sum, max, etc")

    args = parser.parse_args()
    run(args)
