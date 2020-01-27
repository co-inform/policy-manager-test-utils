# Welcome to Policy Manager Test Utils

This repository contains scripts for testing policy manager behaviours.

# Files
All necessary files for testing are under folder ~/data

# How to use test pipeline?

## Step 1 - Generate samples for testing
`sample_generator.py` is method for generating numbers for following modes:


|Mode                          |Description                         |
|-------------------------------|-----------------------------|
|`all_not_verified'`            |All modules have low confidence            |
|`all_agree_all_high`            |All modules agree on same credibility label with high confidence         |
|`some_agree`|Some modules agree on label with high confidence, the rest disagree with low/high confidence|
|`all_agree_some_high`|Some modules agree on label with high confidence, some of them with low confidence|

To generate sample for a mode with default thresholds of the modules run {Mode}:

`python3 sample_generator.py --{Mode}`

To generate sample for a mode with different threshold of specific module, run {Mode} {Module Name}

` python3 sample_generator.py --{Mode} --{Module Name} th1 th2 th3 th4 `

Example:
` python3 sample_generator.py --sample_mode all_not_verified --misinfome_cred 0.5 0.33 -0.24 -0.7 `

## Step 2 - Evaluate specified aggregation function with the samples in ~/data

|Aggregation Function                         |Description                         |
|-------------------------------|-----------------------------|
|`dummy_output`            |Dummy method for just testing the pipeline           |

To evaluate aggregation function run:

`python3 aggregators.py --aggregate_func {Aggregation Function}`

Example:
`python3 aggregators.py --aggregate_func dummy_output`