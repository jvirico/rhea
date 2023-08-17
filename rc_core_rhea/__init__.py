# (c) Copyright 2023 Rico Corp. All rights reserved.
import re
from abc import ABC, abstractmethod

from rich.tree import Tree


class ProvenanceComponent(ABC):
    """
    Abstract class for Pipeline components. Follows Composite design pattern.
    """

    def __init__(self, name: str, attributes: dict[str, str] = {}):
        if not self._is_valid_rdf_string(name):
            raise ValueError(f"Invalid name: {name}")
        self._name = name
        self._attributes: dict[str, str] = {}
        for name, value in attributes.items():
            self.add_attribute(name, value)

    @property
    def name(self) -> str:
        return self._name

    @property
    def attributes(self) -> dict[str, str]:
        return self._attributes

    @abstractmethod
    def generate_triplets(self) -> list[str]:
        """returns rdf definition of component"""

    @abstractmethod
    def generate_cli_tree(self) -> Tree:
        """return rich.Tree object for CLI representation"""

    @abstractmethod
    def list_component_names(self) -> list[str]:
        """return list of component names"""

    def add_attribute(self, name: str, value: str) -> None:
        if not self._is_valid_rdf_string(name):
            raise ValueError(f"Attribute name '{name}' contains unsupported characters.")
        if not self._is_valid_rdf_string(value):
            raise ValueError(f"Attribute value '{value}' contains unsupported characters.")
        self._attributes[name] = value

    def _is_valid_rdf_string(self, rdf_string: str) -> bool:
        # Check for unsupported characters in the RDF string using regular expressions.
        # We are assuming that valid RDF strings contain only alphanumeric characters and underscores.
        # You can adjust the regular expression to meet your specific requirements.
        return bool(re.match(r"^[a-zA-Z0-9_]+$", rdf_string))

    def _generate_attribute_triplet(self, attribute_name: str, attribute_value: str) -> str:
        triplet = f"""rc:{attribute_name} a rc:Attribute .
rc:{attribute_value} a rc:Value .
rc:{attribute_name}_{attribute_value} a rc:AttributeValue ;
    rc:hasAttribute rc:{attribute_name} ;
    rc:hasValue rc:{attribute_value} .
"""
        return triplet

    def _get_attribute_triplets(self) -> list[str]:
        triplets: list[str] = []
        for attribute_name, attribute_value in self.attributes.items():
            attribute_triplet = self._generate_attribute_triplet(attribute_name, attribute_value)
            triplets.append(attribute_triplet)
        return triplets

    def _get_attvalue_names(self) -> str:
        return " , ".join([f"rc:{name}_{value}" for name, value in self.attributes.items()])

    def save_triplets_to_file(self, filename: str) -> None:
        with open(filename, "w") as file:
            headers = """@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rc: <http://ont.rheaproject.org/prov#> .

<> a owl:Ontology ;
    rdfs:label "rc_core_rhea generated"@en ;
    owl:imports <provenance_squema.ttl> .

"""
            file.write(headers)
            for item in self.generate_triplets():
                file.write(item + "\n")

    @staticmethod
    def clean_duplicated_triplets(triplets: list[str]) -> list[str]:
        unique_triplets: list[str] = []
        for triplet in triplets:
            if triplet not in unique_triplets:
                unique_triplets.append(triplet)
        return unique_triplets


class DataInstance(ProvenanceComponent):
    def __init__(self, name: str, attributes: dict[str, str] = {}):
        super().__init__(name, attributes)

    def generate_triplets(self) -> list[str]:
        triplets: list[str] = []

        # DataOp triplet
        main_triplet = f"rc:{self.name} a rc:DataInstance"
        main_triplet += f' ;\n    rc:prefLabel "{self.name}"@en'
        if self.attributes:
            main_triplet += f" ;\n    rc:hasAttributeValue {self._get_attvalue_names()}"
        main_triplet += " .\n"

        triplets.append(main_triplet)
        # define attribute value relationships
        triplets.extend(self._get_attribute_triplets())

        return sorted(self.clean_duplicated_triplets(triplets))

    def generate_cli_tree(self) -> Tree:
        tree = Tree(f"[red]Instance[/]: {self.name}")
        for name, value in self.attributes.items():
            tree.add(f"[deep_sky_blue4]Att[/]: {name}={value}")
        return tree

    def list_component_names(self) -> list[str]:
        return [self.name]


class DataSet(ProvenanceComponent):
    def __init__(self, name: str, attributes: dict[str, str] = {}):
        super().__init__(name, attributes)
        self._containsData: list[DataInstance] = []

    def add_data_instances(self, data_instances: list[DataInstance]) -> None:
        self._containsData.extend(data_instances)

    def _get_data_instance_names(self) -> str:
        return " , ".join([f"rc:{data_instance.name}" for data_instance in self._containsData])

    def generate_triplets(self) -> list[str]:
        triplets: list[str] = []

        # DataOp triplet
        main_triplet = f"rc:{self.name} a rc:DataSet"
        main_triplet += f' ;\n    rc:prefLabel "{self.name}"@en'
        if self._containsData:
            main_triplet += f" ;\n    rc:containsData {self._get_data_instance_names()}"
        if self.attributes:
            main_triplet += f" ;\n    rc:hasAttributeValue {self._get_attvalue_names()}"
        main_triplet += " .\n"

        triplets.append(main_triplet)
        # define attribute value relationships
        triplets.extend(self._get_attribute_triplets())

        # children triplets
        for data in self._containsData:
            triplets.extend(data.generate_triplets())

        return sorted(self.clean_duplicated_triplets(triplets))

    def generate_cli_tree(self) -> Tree:
        tree = Tree(f"[red]Dataset[/]: {self.name}")

        for data in self._containsData:
            tree.add("[turquoise4]containesData").add(data.generate_cli_tree())

        for name, value in self.attributes.items():
            tree.add(f"[deep_sky_blue4]Att[/]: {name}={value}")

        return tree

    def list_component_names(self) -> list[str]:
        components: list[str] = []
        components.append(self.name)
        for instance in self._containsData:
            components.extend(instance.list_component_names())
        return components


class DataOperation(ProvenanceComponent):
    def __init__(self, name: str, attributes: dict[str, str] = {}):
        super().__init__(name, attributes)
        self._has_inputs: list[DataSet] = []
        self._has_outputs: list[DataSet] = []

    def add_input(self, data_set: list[DataSet]) -> None:
        self._has_inputs.extend(data_set)

    def add_output(self, data_set: list[DataSet]) -> None:
        self._has_outputs.extend(data_set)

    def _get_input_names(self) -> str:
        return " , ".join([f"rc:{input.name}" for input in self._has_inputs])

    def _get_output_names(self) -> str:
        return " , ".join([f"rc:{output.name}" for output in self._has_outputs])

    def generate_triplets(self) -> list[str]:
        triplets: list[str] = []

        # DataOp triplet
        main_triplet = f"rc:{self.name} a rc:DataOperation"
        main_triplet += f' ;\n    rc:prefLabel "{self.name}"@en'
        if self._has_inputs:
            main_triplet += f" ;\n    rc:hasInput {self._get_input_names()}"
        if self._has_outputs:
            main_triplet += f" ;\n    rc:hasOutput {self._get_output_names()}"
        if self.attributes:
            main_triplet += f" ;\n    rc:hasAttributeValue {self._get_attvalue_names()}"
        main_triplet += " .\n"

        triplets.append(main_triplet)
        # define attribute value relationships
        triplets.extend(self._get_attribute_triplets())

        # children triplets
        for input in self._has_inputs:
            triplets.extend(input.generate_triplets())
        for output in self._has_outputs:
            triplets.extend(output.generate_triplets())

        return sorted(self.clean_duplicated_triplets(triplets))

    def generate_cli_tree(self) -> Tree:
        tree = Tree(f"[red]DataOp[/]: {self.name}")

        for data in self._has_inputs:
            tree.add("[turquoise4]hasInput").add(data.generate_cli_tree())
        for data in self._has_outputs:
            tree.add("[turquoise4]hasOutput").add(data.generate_cli_tree())

        for name, value in self.attributes.items():
            tree.add(f"[deep_sky_blue4]Att[/]: {name}={value}")

        return tree

    def list_component_names(self) -> list[str]:
        components: list[str] = []
        components.append(self.name)
        for dset in self._has_inputs:
            components.extend(dset.list_component_names())
        for dset in self._has_outputs:
            components.extend(dset.list_component_names())
        return components


class DataPipeline(ProvenanceComponent):
    """
    Captures the provenance of a data pipeline and generates an RDF definition.
    """

    def __init__(self, name: str, attributes: dict[str, str] = {}):
        super().__init__(name, attributes)
        self._consists_of: list[DataOperation] = []

    def add_data_operations(self, data_operations: list[DataOperation]) -> None:
        self._consists_of.extend(data_operations)

    def _get_dataop_names(self) -> str:
        return " , ".join([f"rc:{data_op.name}" for data_op in self._consists_of])

    def generate_triplets(self) -> list[str]:
        triplets: list[str] = []

        # DataOp triplet
        main_triplet = f"rc:{self.name} a rc:DataPipeline"
        main_triplet += f' ;\n    rc:prefLabel "{self.name}"@en'
        if self._consists_of:
            main_triplet += f" ;\n    rc:consistsOf {self._get_dataop_names()}"
        if self.attributes:
            main_triplet += f" ;\n    rc:hasAttributeValue {self._get_attvalue_names()}"
        main_triplet += " .\n"

        triplets.append(main_triplet)
        # define attribute value relationships
        triplets.extend(self._get_attribute_triplets())

        # children triplets
        for data_op in self._consists_of:
            triplets.extend(data_op.generate_triplets())

        return sorted(self.clean_duplicated_triplets(triplets))

    def generate_cli_tree(self) -> Tree:
        tree = Tree(f"[red]Pipe[/]: {self.name}")

        for data in self._consists_of:
            tree.add("[turquoise4]consistsOf").add(data.generate_cli_tree())

        for name, value in self.attributes.items():
            tree.add(f"[deep_sky_blue4]Att[/]: {name}={value}")

        return tree

    def list_component_names(self) -> list[str]:
        components: list[str] = []
        components.append(self.name)
        for dop in self._consists_of:
            components.extend(dop.list_component_names())
        return components
