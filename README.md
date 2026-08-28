# Datacards template repository

This repository provides a starting point for storing your
[Higgs Combine](https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit/)
datacards.

## Requirements

Since the datacards (besides `txt` files) often include binary files such as ROOT files, the repository is set up to use
[Git Large File Storage](https://git-lfs.com) to track them.
This makes cloning the repository much more efficient.
In case that you do not have `git lfs` installed on your system, please
follow the
[`git lfs` installation instructions](https://github.com/git-lfs/git-lfs#installing).

## Analysis specific instructions

The instructions below include the Combine version, commands used to create RooFit workspaces and the combine commands to produce the analysis measurements. 
All of the relevant options for combine commands are documented as well.

## Physics Model

This section contains a brief description of the physics model used in the analysis and the references to the implementation within combine. Please move the `.py` file with the physics model implementation to the `models` directory.

## Validation CI

This repository includes the CI pipeline designed to assist the datacard validation process. To run the validation replace the template datacards with your datacards in the `input` directory, for more details follow the description on the CAT-STATS [documentation page](https://cms-analysis.docs.cern.ch/code/datacard_validation_ci/).

## Systematics naming conventions

A system for naming systematics uncertainties to streamline analyses combinations and improve datacard readability is described [here](https://gitlab.cern.ch/cms-analysis/general/systematics/-/blob/master/README.md?ref_type=heads). In this step you will produce an YAML file with a analysis-specific systematics dictionary. Please add it to the `input` directory with the name `systematics.yml`, so the pipeline can pick it up.

## Publishing datacards

When the analysis is ready for publication and the validation pipeline is passed, we ask you to follow [this documentation page](https://cms-analysis.docs.cern.ch/code/release_statmodel/) and update the README.md, pipeline settings to prepare the model for the release.
