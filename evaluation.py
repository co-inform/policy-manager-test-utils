import json
import os
from pathlib import Path

import pandas as pd
from sklearn.metrics import accuracy_score, average_precision_score

from aggregators import methods

'''
Pipeline for the evaluation

'''

DATA_DIR = Path(os.path.dirname(os.path.dirname(__file__))) / Path(os.path.basename(os.path.dirname(__file__))) / 'data'

LABELS = {

}


def callback_aggregate(row, mode='dummy_output'):
    dummy_request = _create_request(row)
    response = methods[mode](dummy_request)
    return response


def _create_request(row):
    return {

        'misinfome': {
            'cred': row['misinfome_creds'],
            'conf': row['misinfome_conf']
        },
        'stance': {
            'cred': row['content_analys_creds'],
            'conf': row['content_analys_conf']
        },
        'claim_credibility': {
            'cred': row['claim_creds'],
            'conf': row['claim_conf']
        }

    }


def run():
    target_names = {'credible': 0, 'mostly_credible': 1, 'mostly_not_credible': 2, 'credible_uncertain': 3,
                    'not_credible': 4,
                    'not_verifiable': 5}
    results = {}
    for file_name in DATA_DIR.glob('*.csv'):
        name = file_name.name[:-4]
        results['collection'] = name
        dummy_values = pd.read_csv(file_name, low_memory=False)
        ground_labels = [target_names[value] for value in dummy_values.expected_credible]
        dummy_values['actual_credible'] = dummy_values.apply(lambda row: callback_aggregate(row), axis=1)
        predictions = [target_names[value] for value in dummy_values.actual_credible]
        results['accuracy'] = accuracy_score(ground_labels, predictions)
        results['precision_none'] = average_precision_score(ground_labels, predictions)
        results['precision_micro'] = average_precision_score(ground_labels, predictions, average='micro')
        results['precision_macro'] = average_precision_score(ground_labels, predictions, average='macro')
        name = name + '.json'
        with open(DATA_DIR / name , 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    run()
