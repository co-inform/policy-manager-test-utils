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

`evaluation.py` evaluates specific aggregation function for each cases in ~/data, and outputs results for each cases in format of `.json`.

|Aggregation Function                         |Description                         |
|-------------------------------|-----------------------------|
|`dummy_output`            |Dummy method for just testing the pipeline           |

|Evaluation Metrics                        |Description                         |
|-------------------------------|-----------------------------|
|`precision_macro`            | |
|`recall_macro`            | |
|`fscore_macro`            | |
|`precision_micro`            | |
|`recall_micro`            | |
|`fscore_micro`            | |
|`precision_credible`            | |
|`precision_mostly_credible`            | |
|`precision_mostly_not_credible`            | |
|`precision_credible_uncertain` ||
|`precision_not_credible` ||
|`precision_not_verifiable` ||
|`recall_credible` ||
|`recall_mostly_credible` ||
|`recall_mostly_not_credible` ||
|`recall_credible_uncertain` ||
|`recall_not_credible` ||
|`recall_not_verifiable`||
|`fscore_credible`||
|`fscore_mostly_credible`||
|`fscore_mostly_not_credible`||
|`fscore_credible_uncertain`||
|`fscore_not_credible`||
|`fscore_not_verifiable`||å

To evaluate an aggregation function run:

`python3 evaluation.py --aggregate_func {Aggregation Function}`

Example:
`python3 evaluation.py --aggregate_func dummy_output`