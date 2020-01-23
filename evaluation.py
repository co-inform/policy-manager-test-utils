import os
from pathlib import Path

import pandas as pd

from aggregators import methods

'''
Pipeline for the evaluation

'''

DATA_DIR = Path(os.path.dirname(os.path.dirname(__file__))) / Path(os.path.basename(os.path.dirname(__file__))) / 'data'


def callback_aggregate(row, mode = 'dummy_output'):
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
    for file_name in DATA_DIR.glob('*.csv'):
        dummy_values = pd.read_csv(file_name, low_memory=False)
        ground_labels = dummy_values['expected_credible']
        dummy_values['actual_credible'] = dummy_values.apply(lambda row: callback_aggregate(row), axis = 1)
        print(dummy_values)

        # glued_data = pd.concat([glued_data, x], axis=0)

    pass


## aggregation


# check sepearetly


if __name__ == '__main__':
    run()
