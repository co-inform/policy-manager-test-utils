import argparse
import csv
import os
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import requests
from dotenv import load_dotenv
from loguru import logger

logger.add(sys.stderr, level="INFO")
logger.add("debug.log", level="DEBUG", rotation="500 MB")

np.random.seed(seed=42)

ROOT = Path(os.path.dirname(os.path.dirname(__file__))) / Path(os.path.basename(os.path.dirname(__file__)))
DATA_DIR = ROOT / 'data'
env_path = ROOT / '.env'
load_dotenv(dotenv_path=env_path)

# =================== COINFORM API SETTINGS =================
COINFORM_ENDPOINT = os.getenv('COINFORM_ENDPOINT')
QUERY_ID_REQUEST = COINFORM_ENDPOINT + '/twitter/tweet'
RESPONSE_TWEET = COINFORM_ENDPOINT + '/response/{query_id}/debug'

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
        self.modules = {'misinfome': [self.misinfome_cred, self.misinfome_conf],
                        'content_analys': [self.content_analys_cred, self.content_analys_conf],
                        'claim': [self.claim_cred, self.claim_conf]}


    def _all_agree_helper(self):
        labels = list(self.labels.keys())
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
        data['content_analys_cred'] = np.asarray(content_analys_creds).flatten()
        data['claim_cred'] = np.asarray(claim_creds).flatten()
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

    def some_agree(self):
        '''
        This method creates values that some modules agree, some disagree with high/low confidence
        :return:
        :rtype:
        '''
        dummy_values = pd.DataFrame()
        # if data folder does not exist, create
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)

        for i in range(1, len(self.modules.keys()) + 1):
            data_low_conf = self._some_agree_helper(num_diff_module=i, confidence_density=False)
            dummy_values = dummy_values.append(data_low_conf, ignore_index=True, sort=True)
            data_high_conf = self._some_agree_helper(num_diff_module=i, confidence_density=True)
            dummy_values = dummy_values.append(data_high_conf, ignore_index=True, sort=True)

        # save dummy values {casename}_{module_name}_{upboundary_cred}_{conf}
        path = DATA_DIR / '{func_name}_misinfome_{misinfome_cred}_{misinfome_conf}_contentanalysis_{content_analysis_cred}_{content_analysis_conf}_claim_{claim_cred}_{claim_conf}.csv'.format(
            func_name=self.some_agree.__name__,
            misinfome_cred=str(self.misinfome_cred[0]), misinfome_conf=str(self.misinfome_conf),
            content_analysis_conf=self.content_analys_conf, content_analysis_cred=self.content_analys_cred[0],
            claim_cred=str(self.claim_cred[0]), claim_conf=self.claim_conf)
        dummy_values.to_csv(path)

    def _some_agree_helper(self, num_diff_module, confidence_density):
        '''
        :param num_diff_module: number of modules which disgree
        :type num_diff_module: int
        :param confidence_density: confidence density of disagreed modules. If it is true, modules disagree with high confidence
        :type: boolean
        :return:
        :rtype:
        '''
        #### 2 modules agree, one is not ######
        random_modules = self._pick_random_modules(num_diff_module=num_diff_module)
        agreed_modules = random_modules['agree']
        disagreed_modules = random_modules['disagree']
        labels = list(self.labels.keys())
        temp_creds = {'misinfome': [], 'content_analys': [], 'claim': []}
        temp_confs = {'misinfome': [], 'content_analys': [], 'claim': []}
        cred_labels = []
        data = pd.DataFrame()
        print('Agreed modules {}'.format(agreed_modules))
        print('Disagreed modules {}'.format(disagreed_modules))
        for i in range(0, len(self.labels.keys()) - 1):
            if i == 0:
                for agreed_module in agreed_modules:
                    temp_creds[agreed_module].append(np.random.uniform(high=1, low=self.modules[agreed_module][0][i],
                                                                       size=self.total_sample))
                    # high confidence
                    temp_confs[agreed_module].append(
                        np.random.uniform(high=1, low=self.modules[agreed_module][1], size=self.total_sample))

                    # agreed module -> credible, disagreed modules  -> mostly credible (i+1), but disagree module's label is not final.
                for disagreed_module in disagreed_modules:
                    temp_creds[disagreed_module].append(np.random.uniform(high=self.modules[disagreed_module][0][i],
                                                                          low=self.modules[disagreed_module][0][i + 1],
                                                                          size=self.total_sample))
                    temp_confs[disagreed_module].append(
                        np.random.uniform(high=1, low=self.modules[disagreed_module][1],
                                          size=self.total_sample)) if confidence_density else temp_confs[
                        disagreed_module].append(
                        np.random.uniform(high=self.modules[disagreed_module][1], low=0, size=self.total_sample))

                cred_labels.append(np.asarray([labels[i] for _ in range(self.total_sample)]))

            elif i == 4:
                for agreed_module in agreed_modules:
                    temp_creds[agreed_module].append(np.random.uniform(high=self.modules[agreed_module][0][i - 1],
                                                                       low=-1,
                                                                       size=self.total_sample))
                    # high confidence
                    temp_confs[agreed_module].append(
                        np.random.uniform(high=1, low=self.modules[agreed_module][1], size=self.total_sample))
                    # agreed module -> not credible, disagreed modules -> credible uncertain (i-1)
                for disagreed_module in disagreed_modules:
                    temp_creds[disagreed_module].append(np.random.uniform(high=self.modules[disagreed_module][0][i - 1],
                                                                          low=self.modules[disagreed_module][0][i - 2],
                                                                          size=self.total_sample))
                    temp_confs[disagreed_module].append(
                        np.random.uniform(high=1, low=self.modules[disagreed_module][1],
                                          size=self.total_sample)) if confidence_density else temp_confs[
                        disagreed_module].append(
                        np.random.uniform(high=self.modules[disagreed_module][1], low=0, size=self.total_sample))
                cred_labels.append(np.asarray([labels[i] for _ in range(self.total_sample)]))
            else:
                for agreed_module in agreed_modules:
                    temp_creds[agreed_module].append(np.random.uniform(high=self.modules[agreed_module][0][i - 1],
                                                                       low=self.modules[agreed_module][0][i],
                                                                       size=
                                                                       self.total_sample))
                    # high confidence
                    temp_confs[agreed_module].append(
                        np.random.uniform(high=1, low=self.modules[agreed_module][1], size=self.total_sample))
                    # disagreed module -> preeceding (i-1)
                for disagreed_module in disagreed_modules:
                    # preeceding label
                    temp_creds[disagreed_module].append(np.random.uniform(high=self.modules[disagreed_module][0][i - 1],
                                                                          low=self.modules[disagreed_module][0][i - 2],
                                                                          size=
                                                                          self.total_sample))
                    temp_confs[disagreed_module].append(
                        np.random.uniform(high=1, low=self.modules[disagreed_module][1],
                                          size=self.total_sample)) if confidence_density else temp_confs[
                        disagreed_module].append(
                        np.random.uniform(high=self.modules[disagreed_module][1], low=0, size=self.total_sample))
                cred_labels.append(np.asarray([labels[i] for _ in range(self.total_sample)]))

        for name, values in temp_creds.items():
            data[name + '_cred'] = np.asarray(values).flatten()
            data[name + '_conf'] = np.asarray(temp_confs[name]).flatten()
        data['expected_credible'] = np.asarray(cred_labels).flatten()
        return data

    def all_agree_all_high(self):
        '''
        In this case all of modules agree on one credibility label with high confidence
        '''
        dummy_values = pd.DataFrame()
        # if data folder does not exist, create
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)

        data = self._all_agree_helper()

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

    def all_agree_some_high(self):
        '''
        In this case all of modules agree on one credibility label, but some of them with high confidence
        '''
        dummy_values = pd.DataFrame()
        # if data folder does not exist, create
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)

        data = self._all_agree_helper()

        misinfo_conf = []
        content_analys_conf = []
        claim_conf = []
        # confidence value always high between th>val>1 half high
        high_conf_sample = data.shape[0] // 2
        low_conf_sample = data.shape[0] - high_conf_sample

        misinfo_conf.append(np.random.uniform(high=1, low=self.misinfome_conf, size=[high_conf_sample]))

        content_analys_conf.append(np.random.uniform(high=1, low=self.content_analys_conf,
                                                     size=high_conf_sample))
        claim_conf.append(np.random.uniform(high=1, low=self.claim_conf, size=high_conf_sample))

        # confidence value always low val>0
        misinfo_conf.append(np.random.uniform(high=self.misinfome_conf, low=0, size=low_conf_sample))
        content_analys_conf.append(np.random.uniform(high=self.content_analys_conf, low=0,
                                                     size=low_conf_sample))
        claim_conf.append(np.random.uniform(high=self.claim_conf, low=0, size=low_conf_sample))

        data['misinfome_conf'] = np.asarray(misinfo_conf).flatten()
        data['content_analys_conf'] = np.asarray(content_analys_conf).flatten()
        data['claim_conf'] = np.asarray(claim_conf).flatten()

        dummy_values = dummy_values.append(data, ignore_index=True, sort=True)
        # save dummy values {casename}_{module_name}_{upboundary_cred}_{conf}
        path = DATA_DIR / '{func_name}_misinfome_{misinfome_cred}_{misinfome_conf}_contentanalysis_{content_analysis_cred}_{content_analysis_conf}_claim_{claim_cred}_{claim_conf}.csv'.format(
            func_name=self.all_agree_some_high.__name__,
            misinfome_cred=str(self.misinfome_cred[0]), misinfome_conf=str(self.misinfome_conf),
            content_analysis_conf=self.content_analys_conf, content_analysis_cred=self.content_analys_cred[0],
            claim_cred=str(self.claim_cred[0]), claim_conf=self.claim_conf)
        dummy_values.to_csv(path)

    def all_not_verified(self):
        '''
        All of them have low confidence or either fail
        todo: fail case is not implemented
        '''
        dummy_values = pd.DataFrame()
        # if data folder does not exist, create
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
        data = self._all_agree_helper()

        # all of them has low confidence, hence they are unverified.
        data['misinfome_conf'] = np.random.uniform(high=self.misinfome_conf, low=0, size=[data.shape[0]]).flatten()
        data['content_analys_conf'] = np.random.uniform(high=self.content_analys_conf, low=0,
                                                        size=[data.shape[0]]).flatten()
        data['claim_conf'] = np.random.uniform(high=self.claim_conf, low=0, size=[data.shape[0]]).flatten()

        # label credibility
        data['expected_credible'] = 'not_verifiable'

        dummy_values = dummy_values.append(data, ignore_index=True, sort=True)
        # save dummy values {casename}_{module_name}_{upboundary_cred}_{conf}
        path = DATA_DIR / '{func_name}_misinfome_{misinfome_cred}_{misinfome_conf}_contentanalysis_{content_analysis_cred}_{content_analysis_conf}_claim_{claim_cred}_{claim_conf}.csv'.format(
            func_name=self.all_agree_some_high.__name__,
            misinfome_cred=str(self.misinfome_cred[0]), misinfome_conf=str(self.misinfome_conf),
            content_analysis_conf=self.content_analys_conf, content_analysis_cred=self.content_analys_cred[0],
            claim_cred=str(self.claim_cred[0]), claim_conf=self.claim_conf)
        dummy_values.to_csv(path)

    def _map_label(self, label):
        print('Not implemented yet!!')
        return None

    def _request(self, tweet_id):
        # logger.debug('I am requesting tweet {}'.format(tweet_id))
        args = {
            "tweet_id": parse_id(tweet_id),
            "tweet_author": "string",
            "tweet_text": "string"
        }
        # first response includes query id
        response_1 = requests.post(QUERY_ID_REQUEST, json=args).json()
        if 'query_id' not in response_1:
            return None
        query_id = response_1['query_id']
        task_completed = False
        modules_response = {}

        err_count = 100
        while (not task_completed):
            response_2 = requests.get(RESPONSE_TWEET.format(query_id=query_id)).json()
            status = response_2['status']
            # logger.debug('Query response {}'.format(status))
            if status == 'partly_done' or status == 'in_progress':
                err_count -= 1
                if err_count == 0:
                    status = 'done'
            if status == 'done':
                response_codes = response_2['module_response_code']
                logger.debug(response_2['flattened_module_responses'])
                if response_codes[
                    'claimcredibility'] == 200 and 'claimcredibility_tweet_claim_credibility_0_confidence' in \
                        response_2['flattened_module_responses']:
                    modules_response['claim_conf'] = response_2['flattened_module_responses'][
                        'claimcredibility_tweet_claim_credibility_0_confidence']
                    modules_response['claim_cred'] = response_2['flattened_module_responses'][
                        'claimcredibility_tweet_claim_credibility_0_credibility']
                else:
                    modules_response['claim_conf'] = -100
                    modules_response['claim_cred'] = -100
                if response_codes['contentanalysis'] == 200 and 'contentanalysis_credibility' in response_2[
                    'flattened_module_responses']:
                    modules_response['content_analys_conf'] = response_2['flattened_module_responses'][
                        'contentanalysis_confidence']
                    modules_response['content_analys_cred'] = response_2['flattened_module_responses'][
                        'contentanalysis_credibility']
                else:
                    modules_response['content_analys_conf'] = -100
                    modules_response['content_analys_cred'] = -100
                if response_codes['misinfome'] == 200 and 'misinfome_credibility_value' in response_2[
                    'flattened_module_responses']:
                    modules_response['misinfome_conf'] = response_2['flattened_module_responses'][
                        'misinfome_credibility_confidence']
                    modules_response['misinfome_cred'] = response_2['flattened_module_responses'][
                        'misinfome_credibility_value']
                else:
                    modules_response['misinfome_conf'] = -100
                    modules_response['misinfome_cred'] = -100

                task_completed = True

        return modules_response

    def export_to_file(self, row, file_path):
        with open(file_path, 'a', encoding='utf-8') as f:
            cw = csv.writer(f, delimiter='\t')
            cw.writerow(row)

    def from_misinfome(self):
        '''
        Retrieves english tweets from misinfome collection and record tweet ids and labels.
        :return:
        :rtype:
        '''
        dest_file = DATA_DIR / 'misinfome.tsv'
        src_file = DATA_DIR / 'misinfome' / 'joined_tables.tsv'
        fc_labels_file = DATA_DIR / 'misinfome' / 'fact_checking_gold_labels.tsv'
        responses_file = DATA_DIR / 'misinfome' / 'misinfome_responses.csv'
        file_path = DATA_DIR / 'misinfome/rule-responses/export.csv'

        if not os.path.isfile(dest_file):
            data = pd.read_csv(src_file, sep='\t')
            mask = (data['lang'] == 'en') & (data['source'].str.contains('twitter'))
            data = data[mask]
            data = data[['url', 'factchecker_label']]
            if not fc_labels_file.exists():
                fc_labels = pd.DataFrame(pd.unique(data['factchecker_label']))
                fc_labels.to_csv(fc_labels_file)

            ## claim_conf,claim_cred,content_analys_conf,content_analys_cred,expected_credible,misinfome_conf,misinfome_cred
            if not responses_file.exists():
                self.export_to_file(['#id', 'url', 'claim_conf',
                                     'claim_cred',
                                     'content_analys_conf',
                                     'content_analys_cred',
                                     'misinfome_conf',
                                     'misinfome_cred'], file_path)
                for index, row in data.iterrows():
                    row['id'] = parse_id(row['url'])
                    logger.info(row['id'])
                    response = self._request(row['url'])
                    if response:
                        row_obj = {
                            'id': row['id'],
                            'url': row['url'],
                            'claim_conf': response['claim_conf'],
                            'claim_cred': response['claim_cred'],
                            'content_analys_conf': response['content_analys_conf'],
                            'content_analys_cred': response['content_analys_cred'],
                            'misinfome_conf': response['misinfome_conf'],
                            'misinfome_cred': response['misinfome_cred'],
                        }
                        # row['expected_credible'] = self._map_label(row['factchecker_label'])
                        self.export_to_file(list(row_obj.values()), file_path)
                # data[['claim_conf', 'claim_cred', 'content_analys_conf', 'content_analys_cred', 'misinfome_conf',
                #       'misinfome_cred']].to_csv(responses_file)
            # todo add final data csv


if __name__ == '__main__':
    print('This script generates samples for testing rules')
    parser = argparse.ArgumentParser()
    parser.add_argument('--n_samples', type=int, default=20)
    parser.add_argument('--misinfome_cred', action='store',
                        type=float, nargs=4, default=[0.66, 0.33, -0.33, -0.66],
                        help="Examples: --misinfome_cred item1 item2")
    parser.add_argument('--content_analysis_cred', action='store',
                        type=float, nargs=4, default=[0.6, 0.3, -0.3, -0.6],
                        help="Examples: --content_analysis_cred item1 item2")
    parser.add_argument('--claim_cred', action='store',
                        type=float, nargs=4, default=[0.5, 0.25, -0.5, -0.25],
                        help="Examples: --claim_cred item1 item2")
    parser.add_argument('--misinfome_conf',
                        type=float, default=0.5)
    parser.add_argument('--content_analysis_conf',
                        type=float, default=0.6)
    parser.add_argument('--claim_conf', type=float, default=0.7)
    parser.add_argument('--n_modules', type=int, default=3, help="total number of modules")
    parser.add_argument('--sample_mode', type=str, default='external_misinfome',
                        help="select sample mode, all_not_verified, all_agree_all_high or some agree")

    args = parser.parse_args()
    sample_gen = Sample_Generator(args)
    mode = args.sample_mode

    print('Selected mode is {}'.format(mode))

    if mode == 'all_not_verified':
        sample_gen.all_not_verified()
    elif mode == 'all_agree_all_high':
        sample_gen.all_agree_all_high()
    elif mode == 'some_agree':
        sample_gen.some_agree()
    elif mode == 'all_agree_some_high':
        sample_gen.all_agree_some_high()
    elif mode == 'external_misinfome':
        sample_gen.from_misinfome()
