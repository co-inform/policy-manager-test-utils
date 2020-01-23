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
    misinfome_creds = args.misinfome_cred
    content_analys_cred = args.content_analysis_cred
    claim_cred = args.claim_cred

    # confidences
    misinfome_conf = args.misinfome_conf
    content_analys_conf = args.content_analysis_conf
    claim_conf = args.claim_conf

    # agreement
    agreement = args.agreement

    # confidence density -> boolean true means high confidence, false means low confidence
    confidence_high = args.confidence_high

    # initialize json for results
    columns = ['misinfome_cred',
               'misinfome_conf',
               'content_analysis_cred',
               'content_analysis_conf',
               'claim_conf',
               'claim_cred',
               'agreement',
               'confidence_density']

    dummy_values = pd.DataFrame(columns=columns)

    # all modules "agree" with high confidence
    if agreement == total_modules and confidence_high:
        # credible
        dummy_values.misinfome_cred.apply(np.random.sample(total_sample).uniform(misinfome_creds[0], misinfome_creds[1]))
        print(dummy_values.misinfome_cred)

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
    parser.add_argument('--agreement', type=int, default=3,
                        help="If n module exists, and agreement is equal to m (e.g), m module agrees, n-m module disagrees")
    parser.add_argument('--confidence_high', type=bool, default=True)

    args = parser.parse_args()
    sample_generator(args)
