![Rhea Banner](/img/rhea.png)

# Rhea

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-3100/)
[![GitHub stars](https://img.shields.io/github/stars/jvirico/rhea)](https://github.com/jvirico/rhea/stargazers)
[![GitHub issues](https://img.shields.io/github/issues/jvirico/rhea)](https://github.com/jvirico/rhea/issues)

Rhea is a Python tool designed to model the provenance at various granularity levels: dataset, feature, attribute, and data transformation. It's built upon the standards set by the W3C and adheres to the RDF format, ensuring a consistent and reliable representation of provenance information.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Contribute](#contribute)
- [License](#license)


## Features

- Model provenance at multiple levels: dataset, feature, attribute, and data transformation.
- Built upon W3C standards and RDF format.
- Intuitive Python API for smooth integration into data pipelines.
- Export and save your provenance models in standard formats.

## Installation

```bash
git clone git@github.com:jvirico/rhea.git
cd rhea
conda create -n rhea poetry python=3.10
conda activate rhea
poetry install
```


## Usage
Here's a quick start guide to get you going:
```shell
poetry run python -m rc_core_rhea -o output/path/provenance.ttl
```

## Provenance example

**Pipeline Objective**: Process a local folder, enrich it with metadata, and register it to a Data Catalog.
<br/>

![Rhea Banner](/img/1_step_pipe.png)
<div align="center">
Fig.1 - Logical representation of process.
</div>


<br/>

![Rhea Banner](/img/1_step_pipe_provenance.png)
<div align="center">
Fig.2 - Provenance representation of process.
</div>


<br/>

To represent the provenance of this simple pipeline, we use the next Rhea CLI options:
> 1. `Create Dataset`
>    - name = *local_folder_dataset*
> 2. `Create Dataset`
>    - name = *R0000013_2023_08_14_my_dataset*
>    - `Attribute`
>       - name = *version*, value = *1*
> 3. `Create DataOperation`
>    - name = *ch_core_mlops_dataset_register*
>    - `Attribute`
>       - name = *release*, value = *0_0_1*
>    - `hasInput`: *local_folder_dataset*
>    - `hasOutput`: *R0000013_2023_08_14_my_dataset*
> 4. `Save & Exit`

<br/>
<br/>

Which is represented as a tree in Rhea CLI interface:

![Rhea Banner](/img/1_step_pipe_tree.png)
<div align="center">
Fig.3 - Tree representation in CLI UI.
</div>


<br/>
<br/>

We will obtain the following `provenance.ttl` definition:
```
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rc: <http://ont.rheaproject.org/prov#> .

<> a owl:Ontology ;
    rdfs:label "rc_core_rhea generated"@en ;
    owl:imports <provenance_squema.ttl> .

rc:R0000013_2023_08_14_my_dataset a rc:DataSet ;
    rc:prefLabel "R0000013_2023_08_14_my_dataset"@en ;
    rc:hasAttributeValue rc:version_1 .

rc:ch_core_mlops_dataset_register a rc:DataOperation ;
    rc:prefLabel "ch_core_mlops_dataset_register"@en ;
    rc:hasInput rc:local_folder_dataset ;
    rc:hasOutput rc:R0000013_2023_08_14_my_dataset ;
    rc:hasAttributeValue rc:release_0_0_1 .

rc:local_folder_dataset a rc:DataSet ;
    rc:prefLabel "local_folder_dataset"@en .

rc:pipe_12282 a rc:DataPipeline ;
    rc:prefLabel "pipe_12282"@en ;
    rc:consistsOf rc:ch_core_mlops_dataset_register .

rc:release a rc:Attribute .
rc:0_0_1 a rc:Value .
rc:release_0_0_1 a rc:AttributeValue ;
    rc:hasAttribute rc:release ;
    rc:hasValue rc:0_0_1 .

rc:version a rc:Attribute .
rc:1 a rc:Value .
rc:version_1 a rc:AttributeValue ;
    rc:hasAttribute rc:version ;
    rc:hasValue rc:1 .
```

<br/>

## Contribute
We welcome contributions! Please see our [contribution guidelines]() for more details.



## License
This project is licensed under the MIT License. See the [LICENSE.md](LICENSE) file for details.


---
<sup>Made with :heart: by [jvirico](https://jvirico.github.io/cv/)</sup>