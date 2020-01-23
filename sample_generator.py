import argparse

import numpy as np
import pandas as pd


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

    index = total_sample
    # credible
    # credibility values
    dummy_values.loc[:index, 'misinfome_creds'] = np.random.uniform(high=1, low=misinfome_cred[0], size=[total_sample])
    dummy_values.loc[:index, 'content_analys_creds'] = np.random.uniform(high=1, low=content_analys_cred[0],
                                                                         size=[total_sample])
    dummy_values.loc[:index, 'claim_creds'] = np.random.uniform(high=1, low=claim_cred[0], size=[total_sample])
    # confidence value
    dummy_values.loc[:index, 'misinfome_conf'] = np.random.randint(high=1, low=misinfome_conf, size=[total_sample])
    dummy_values.loc[:index, 'content_analys_conf'] = np.random.randint(high=1, low=content_analys_conf,
                                                                        size=[total_sample])
    dummy_values.loc[:index, 'claim_conf'] = np.random.randint(high=1, low=claim_conf, size=[total_sample])
    # agreement
    dummy_values.loc[:index, 'agreement'] = np.random.randint(high=total_modules, low=1, size=[total_sample])
    # confidence_density
    dummy_values.loc[:index, 'confidence_density'] = np.random.randint(high=1, low=0, size=[total_sample])
    # label credibility
    dummy_values.loc[:index, 'expected_credible'] = 'credible'

    print(dummy_values)
    pass


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
