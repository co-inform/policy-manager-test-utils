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


def check_single_module(single_module_result):
    pass

# todo add probabilistic evaluation methods
