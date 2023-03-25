# qodana-reports

This repository contains the reports generated by [Qodana](https://www.jetbrains.com/qodana/) for 
[LizardByte](https://github.com/LizardByte) projects.

## View reports

Reports are listed by project at https://app.lizardbyte.dev/qodana-reports/

## Publishing reports

Reports are automatically published to this repository by our workflows, but there is a limitation.

Reports will be published here once the `dispatcher.yml` workflow exists in the default branch of the project of
interest. This is due to a limitation of GitHub Actions where the default token does not have access to the repository
and cannot find the workflow on non-default branches.

## Adding a new project

To add a new project, create the `qodana-<language>.yml` config files in the repository of interest.

The language names are listed below.

- dotnet
- go
- java
- js
- php
- python

Finally, the repository must have the `ci-qodana.yml` and `dispatcher.yml` workflows. These will be added to each
repository automatically by our `.github` repository, but they can be added manually if necessary.
