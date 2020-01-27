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

def median(credibility_results):
    pass

def maximum(credibility_results):
    pass

methods = {

    'default': default,
    'dummy_output': dummy_output,
    'median': median,
    'maximum': maximum

}
