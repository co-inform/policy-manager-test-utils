# Welcome to Policy Manager Test Utils

This repository contains scripts for testing policy manager behaviours.

# Files
All necessary files for testing are under folder ~/data

## Generate random numbers for testing
`sample_generator.py` is method for generating numbers for following modes:


|Mode                          |Description                         |
|-------------------------------|-----------------------------|
|`all_not_verified'`            |All modules have low confidence            |
|`all_agree_all_high`            |All modules agree on same credibility label with high confidence         |
|`some_agree`|Some modules agree on label with high confidence, the rest disagree with low/high confidence|

To generate sample for a mode, run {Mode}:
`python3 sample_generator.py --{Mode}`