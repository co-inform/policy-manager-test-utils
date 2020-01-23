import argparse
import os
from pathlib import Path

import numpy as np
import pandas as pd

DATA_DIR = Path(os.path.dirname(os.path.dirname(__file__))) / Path(os.path.basename(os.path.dirname(__file__))) / 'data'
LABELS = {'credible': 0, 'mostly_credible': 1, 'mostly_not_credible': 2, 'credible_uncertain': 3,
          'not_credible': 4,
          'not_verifiable': 5}


def sample_generator(args):
    # create samples for one case in, including fails (assign fails with number such as -10)
    # columns of csv as follows:
    # each test values and and labels, expected rule engine label
    # save it into as csv.
    # for each case create n samples

    # =================== Params =================
    total_modules = args.n_modules
    total_sample = args.n_samples

    # credibility boundaries
    misinfome_cred = args.misinfome_cred
    content_analys_cred = args.content_analysis_cred
    claim_cred = args.claim_cred

    # confidences
    misinfome_conf = args.misinfome_conf
    content_analys_conf = args.content_analysis_conf
    claim_conf = args.claim_conf

    dummy_values = pd.DataFrame()

    # if data folder does not exist, create
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    # All agree with high confidence, not verifiable is not included
    labels = list(LABELS.keys())
    for i in range(0, len(labels) - 1):
        data = pd.DataFrame()

        if i == 0:
            data['misinfome_creds'] = np.random.uniform(high=1, low=misinfome_cred[i],
                                                        size=[total_sample])
            data['content_analys_creds'] = np.random.uniform(high=1, low=content_analys_cred[i],
                                                             size=[total_sample])
            data['claim_creds'] = np.random.uniform(high=1, low=claim_cred[i], size=[total_sample])
        elif i == 4:
            data['misinfome_creds'] = np.random.uniform(high=misinfome_cred[i - 1],
                                                        low=-1,
                                                        size=[total_sample])
            data['content_analys_creds'] = np.random.uniform(high=content_analys_cred[i - 1],
                                                             low=-1,
                                                             size=[total_sample])
            data['claim_creds'] = np.random.uniform(high=claim_cred[i - 1], low=-1,
                                                    size=[total_sample])
        else:
            data['misinfome_creds'] = np.random.uniform(high=misinfome_cred[i - 1],
                                                        low=misinfome_cred[i],
                                                        size=[total_sample])
            data['content_analys_creds'] = np.random.uniform(high=content_analys_cred[i - 1],
                                                             low=content_analys_cred[i],
                                                             size=[total_sample])
            data['claim_creds'] = np.random.uniform(high=claim_cred[i - 1], low=claim_cred[i],
                                                    size=[total_sample])

        # confidence value
        data['misinfome_conf'] = np.random.uniform(high=1, low=misinfome_conf, size=[total_sample])
        data['content_analys_conf'] = np.random.uniform(high=1, low=content_analys_conf,
                                                        size=[total_sample])
        data['claim_conf'] = np.random.uniform(high=1, low=claim_conf, size=[total_sample])

        # confidence_density -> all of them have high confidence
        data['confidence_density'] = 1.0
        # label credibility
        data['expected_credible'] = labels[i]

        dummy_values = dummy_values.append(data, ignore_index=True, sort=True)

    # save dummy values {casename}_{module_name}_{upboundary_cred}_{conf}
    path = DATA_DIR / 'all_agree_with_high_misinfome_{misinfome_cred}_{misinfome_conf}_contentanalysis_{content_analysis_cred}_{content_analysis_conf}_claim_{claim_cred}_{claim_conf}.csv'.format(
        misinfome_cred=str(misinfome_cred[0]), misinfome_conf=str(misinfome_conf),
        content_analysis_conf=content_analys_conf, content_analysis_cred=content_analys_cred[0],
        claim_cred=str(claim_cred[0]), claim_conf=claim_conf)

    dummy_values.to_csv(path)


if __name__ == '__main__':
    print('This script generates samples for testing rules')
parser = argparse.ArgumentParser()
parser.add_argument('--n_samples', type=int, default=20)
parser.add_argument('--misinfome_cred', action='store',
                    type=float, nargs='*', default=[0.66, 0.33, -0.33, -0.66],
                    help="Examples: --misinfome_cred item1 item2")
parser.add_argument('--content_analysis_cred', action='store',
                    type=float, nargs='*', default=[0.6, 0.3, -0.3, -0.6],
                    help="Examples: --content_analysis_cred item1 item2")
parser.add_argument('--claim_cred', action='store',
                    type=float, nargs='*', default=[0.5, 0.25, -0.5, -0.25],
                    help="Examples: --claim_cred item1 item2")
parser.add_argument('--misinfome_conf',
                    type=float, default=0.5)
parser.add_argument('--content_analysis_conf',
                    type=float, default=0.6)
parser.add_argument('--claim_conf', type=float, default=0.7)
parser.add_argument('--n_modules', type=int, default=3, help="total number of modules")

args = parser.parse_args()
sample_generator(args)
