import numpy as np

# this is default method

'''
module name: e.g misinfome
result: cred, confidence values, label
get all values and take average, then set it to final label
'''


def default(credibility_results):
    count = 0
    for module_name, result in credibility_results.items():
        if (result.cred):
            pass


def dummy_output(credibility_results):
    labels = ['credible', 'mostly_credible', 'mostly_not_credible', 'credible_uncertain', 'not_credible',
              'not_verifiable']
    random_idx = np.random.randint(high=len(labels), low=0, size=1)[0]
    return labels[random_idx]


def check_single_module(single_module_result):
    pass


# todo add probabilistic evaluation methods


methods = {

    'default': default,
    'dummy_output': dummy_output

}
