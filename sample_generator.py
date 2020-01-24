import argparse
import os
from pathlib import Path

import numpy as np
import pandas as pd

DATA_DIR = Path(os.path.dirname(os.path.dirname(__file__))) / Path(os.path.basename(os.path.dirname(__file__))) / 'data'


class Sample_Generator():
    def __init__(self, args):
        # =================== Params =================
        self.total_modules = args.n_modules
        self.total_sample = args.n_samples

        # credibility boundaries
        self.misinfome_cred = args.misinfome_cred
        self.content_analys_cred = args.content_analysis_cred
        self.claim_cred = args.claim_cred

        # confidences
        self.misinfome_conf = args.misinfome_conf
        self.content_analys_conf = args.content_analysis_conf
        self.claim_conf = args.claim_conf
        self.labels = {'credible': 0, 'mostly_credible': 1, 'mostly_not_credible': 2, 'credible_uncertain': 3,
                       'not_credible': 4,
                       'not_verifiable': 5}
        self.modules = {'misinfome_creds': self.misinfome_cred, 'content_analys_creds': self.content_analys_cred,
                        'claim_creds': self.claim_cred}

    def _all_agree_helper(self, labels):
        data = pd.DataFrame()
        misinfome_creds = []
        content_analys_creds = []
        claim_creds = []
        cred_labels = []

        for i in range(0, len(labels) - 1):
            if i == 0:
                misinfome_creds.append(np.random.uniform(high=1, low=self.misinfome_cred[i],
                                                         size=self.total_sample))
                content_analys_creds.append(np.random.uniform(high=1,
                                                              low=self.content_analys_cred[i],
                                                              size=[self.total_sample]))
                claim_creds.append(np.random.uniform(high=1, low=self.claim_cred[i],
                                                     size=[self.total_sample]))
                cred_labels.append(np.asarray([labels[i] for _ in range(self.total_sample)]))

            elif i == 4:
                misinfome_creds.append(np.random.uniform(high=self.misinfome_cred[i - 1],
                                                         low=-1,
                                                         size=[self.total_sample]))
                content_analys_creds.append(np.random.uniform(high=self.content_analys_cred[i - 1],
                                                              low=-1,
                                                              size=[self.total_sample]))
                claim_creds.append(np.random.uniform(high=self.claim_cred[i - 1], low=-1,
                                                     size=[self.total_sample]))
                cred_labels.append(np.asarray([labels[i] for _ in range(self.total_sample)]))
            else:

                misinfome_creds.append(np.random.uniform(high=self.content_analys_cred[i - 1],
                                                         low=self.content_analys_cred[i],
                                                         size=[self.total_sample]))
                content_analys_creds.append(np.random.uniform(high=self.content_analys_cred[i - 1],
                                                              low=self.content_analys_cred[i],
                                                              size=[self.total_sample]))
                claim_creds.append(np.random.uniform(high=self.claim_cred[i - 1],
                                                     low=self.claim_cred[i], size=[self.total_sample]))
                cred_labels.append(np.asarray([labels[i] for _ in range(self.total_sample)]))

        data['misinfome_cred'] = np.asarray(misinfome_creds).flatten()
        data['content_analys_creds'] = np.asarray(content_analys_creds).flatten()
        data['claim_creds'] = np.asarray(claim_creds).flatten()
        data['expected_credible'] = np.asarray(cred_labels).flatten()

        return data

    def _pick_random_modules(self, num_diff_module):
        '''
        :param num_module: number of module which has different functions
        :type num_module: int
        :return:
        :rtype:
        '''
        all_idxs = set([i for i in range(len(self.modules.keys()))])
        disagree_idxs = set()
        picked_flag = False
        for i in range(num_diff_module):
            while not picked_flag:
                picked_num = np.random.randint(high=len(self.modules.keys()), low=0, size=1)[0]
                if picked_num not in disagree_idxs:
                    disagree_idxs.add(picked_num)
                    picked_flag = True

        agree_idxs = all_idxs - disagree_idxs
        return {'agree': [list(self.modules.keys())[agree_idx] for agree_idx in agree_idxs],
                'disagree': [list(self.modules.keys())[disagree_idx] for disagree_idx in disagree_idxs]}

    def _pick_random_label(self, idx_agreed):
        labels = list(self.labels.keys())
        picked_flag = False
        picked_id = None
        while (not picked_flag):
            random_idx = np.random.randint(high=len(labels), low=0, size=1)[0]
            if random_idx is not idx_agreed:
                picked_id = random_idx
                picked_flag = True

        return labels[picked_id]

    def some_agree_without_fail(self):
        #### 2 modules agree, one is not ######
        random_modules = self._pick_random_modules(num_diff_module=2)
        agreed_modules = random_modules['agree']
        disagreed_modules = random_modules['disagree']
        labels = list(self.labels.keys())

        for i in range(0, len(self.labels.keys()) - 1):
            data = pd.DataFrame()

            if i == 0:
                for idx, agreed_module in enumerate(agreed_modules):
                    data[agreed_module] = np.random.uniform(high=1, low=self.modules[agreed_module][i],
                                                            size=[self.total_sample])
                    data['expected_credible'] = labels[i]


            elif i == 4:
                for agreed_module in agreed_modules:
                    data[agreed_module] = np.random.uniform(high=self.modules[agreed_module][i - 1],
                                                            low=-1,
                                                            size=[self.total_sample])
                    data['expected_credible'] = labels[i]
            else:
                for agreed_module in agreed_modules:
                    data[agreed_module] = np.random.uniform(high=self.modules[agreed_module][i - 1],
                                                            low=self.modules[agreed_module][i],
                                                            size=[
                                                                self.total_sample])
                    data['expected_credible'] = labels[i]
        print(data)

        return data

    def all_agree_all_high(self):
        '''
        In this case all of modules agree on one credibility label with high confidence
        '''
        dummy_values = pd.DataFrame()
        # if data folder does not exist, create
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)

        labels = list(self.labels.keys())
        data = self._all_agree_helper(labels)

        # confidence value always high between th>val>1
        data['misinfome_conf'] = np.random.uniform(high=1, low=self.misinfome_conf, size=[data.shape[0]])
        data['content_analys_conf'] = np.random.uniform(high=1, low=self.content_analys_conf,
                                                        size=[data.shape[0]])
        data['claim_conf'] = np.random.uniform(high=1, low=self.claim_conf, size=[data.shape[0]])

        dummy_values = dummy_values.append(data, ignore_index=True, sort=True)
        # save dummy values {casename}_{module_name}_{upboundary_cred}_{conf}
        path = DATA_DIR / '{func_name}_misinfome_{misinfome_cred}_{misinfome_conf}_contentanalysis_{content_analysis_cred}_{content_analysis_conf}_claim_{claim_cred}_{claim_conf}.csv'.format(
            func_name=self.all_agree_all_high.__name__,
            misinfome_cred=str(self.misinfome_cred[0]), misinfome_conf=str(self.misinfome_conf),
            content_analysis_conf=self.content_analys_conf, content_analysis_cred=self.content_analys_cred[0],
            claim_cred=str(self.claim_cred[0]), claim_conf=self.claim_conf)
        dummy_values.to_csv(path)

    def all_not_verified(self):
        '''
        All of them have low confidence or either fail
        '''
        dummy_values = pd.DataFrame()
        # if data folder does not exist, create
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
        data = self._all_agree_helper()
        # todo add some of agree
        # todo add failed ones
        # all of them has low confidence, hence they are unverified.
        data.loc['misinfome_conf'] = np.random.uniform(high=1, low=self.misinfome_conf, size=[self.total_sample])
        data.loc['content_analys_conf'] = np.random.uniform(high=1, low=self.content_analys_conf,
                                                            size=[self.total_sample])
        data.loc['claim_conf'] = np.random.uniform(high=1, low=self.claim_conf, size=[self.total_sample])

        # label credibility
        data['expected_credible'] = 'not_verifiable'

        dummy_values = dummy_values.append(data, ignore_index=True, sort=True)
        # save dummy values {casename}_{module_name}_{upboundary_cred}_{conf}
        path = DATA_DIR / '{func_name}_misinfome_{misinfome_cred}_{misinfome_conf}_contentanalysis_{content_analysis_cred}_{content_analysis_conf}_claim_{claim_cred}_{claim_conf}.csv'.format(
            func_name=self.all_not_verified.__name__,
            misinfome_cred=str(self.misinfome_cred[0]), misinfome_conf=str(self.misinfome_conf),
            content_analysis_conf=self.content_analys_conf, content_analysis_cred=self.content_analys_cred[0],
            claim_cred=str(self.claim_cred[0]), claim_conf=self.claim_conf)
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
    sample_gen = Sample_Generator(args)
    # sample_gen.all_not_verified()
    sample_gen.all_agree_all_high()
    # sample_gen.some_agree_without_fail()
