# (c) Copyright 2023 Rico Corp. All rights reserved.
from pathlib import Path
import pytest

from rc_core_rhea import ProvenanceComponent, DataInstance, DataOperation, DataPipeline, DataSet
from rich.tree import Tree


class ConcreteComponent(ProvenanceComponent):
    def generate_triplets(self) -> list[str]:
        """returns rdf definition of component"""
        pass

    def generate_cli_tree(self) -> Tree:
        """return rich.Tree object for CLI representation"""
        pass

    def list_component_names(self) -> list[str]:
        """return list of component names"""
        pass


def test_invalid_rdf_string():
    with pytest.raises(ValueError):
        DataInstance("Invalid Name!")


def test_rdf_string_validation():
    valid_name = "validName_123"
    invalid_name = "invalid name!"

    # Testing a valid name
    ConcreteComponent(valid_name)

    # Testing an invalid name
    with pytest.raises(ValueError):
        ConcreteComponent(invalid_name)


def test__data_instance__adding_invalid_attributes():
    with pytest.raises(ValueError):
        DataInstance("Instance", {"invalid name": "value"})

    with pytest.raises(ValueError):
        DataInstance("Instance", {"name": "invalid value"})


def test__data_instance__methods():
    instance = DataInstance("instance1", {"attr1": "value1"})
    assert instance.name == "instance1"
    assert instance.attributes == {"attr1": "value1"}

    # Test the generate_triplets function
    triplets = instance.generate_triplets()
    assert isinstance(triplets, list)

    # Test CLI tree representation
    cli_tree = instance.generate_cli_tree()
    assert cli_tree.label == "[red]Instance[/]: instance1"

    # Test list_component_names function
    names = instance.list_component_names()
    assert names == ["instance1"]


def test__data_set__methods():
    instance1 = DataInstance("instance1", {"attr1": "value1"})
    instance2 = DataInstance("instance2", {"attr2": "value2"})

    dataset = DataSet("dataset1")
    dataset.add_data_instances([instance1, instance2])

    # Test the generate_triplets function
    triplets = dataset.generate_triplets()
    assert isinstance(triplets, list)

    # Test CLI tree representation
    cli_tree = dataset.generate_cli_tree()
    assert cli_tree.label == "[red]Dataset[/]: dataset1"

    # Test list_component_names function
    names = dataset.list_component_names()
    assert set(names) == {"dataset1", "instance1", "instance2"}


def test__data_operation__methods():
    dataset1 = DataSet("dataset1")
    dataset2 = DataSet("dataset2")

    operation = DataOperation("operation1")
    operation.add_input([dataset1])
    operation.add_output([dataset2])

    # Test the generate_triplets function
    triplets = operation.generate_triplets()
    assert isinstance(triplets, list)

    # Test CLI tree representation
    cli_tree = operation.generate_cli_tree()
    assert cli_tree.label == "[red]DataOp[/]: operation1"

    # Test list_component_names function
    names = operation.list_component_names()
    assert set(names) == {"operation1", "dataset1", "dataset2"}


def test__data_pipeline__methods():
    operation1 = DataOperation("operation1")
    operation2 = DataOperation("operation2")

    pipeline = DataPipeline("pipeline1")
    pipeline.add_data_operations([operation1, operation2])

    # Test the generate_triplets function
    triplets = pipeline.generate_triplets()
    assert isinstance(triplets, list)

    # Test CLI tree representation
    cli_tree = pipeline.generate_cli_tree()
    assert cli_tree.label == "[red]Pipe[/]: pipeline1"

    # Test list_component_names function
    names = pipeline.list_component_names()
    assert set(names) == {"pipeline1", "operation1", "operation2"}


def test__data_instance__save_triplets_to_file(tmp_path):
    instance = DataInstance("Instance1", {"attribute1": "value1"})
    file = tmp_path / "triplets.txt"
    instance.save_triplets_to_file(file)

    assert file.read_text().count("\n") > 0  # Ensure something was written to the file


def test__provenance_component__clean_duplicated_triplets():
    triplets = ["triplet1", "triplet2", "triplet1", "triplet3", "triplet2"]
    cleaned = ProvenanceComponent.clean_duplicated_triplets(triplets)
    assert set(cleaned) == set(["triplet1", "triplet2", "triplet3"])


def test__data_pipeline__full_sample(tmp_path: Path) -> None:
    ins1 = DataInstance("0000001_png")
    ins2 = DataInstance("0000002_png")
    ins3 = DataInstance("0000003_png")
    ins4 = DataInstance("0000004_png")
    ins5 = DataInstance("0000005_png")
    ins5.add_attribute("annotated", "no")
    ins6 = DataInstance("0000006_png")
    ins6.add_attribute("annotated", "no")

    ds1 = DataSet("D00000001_2023")
    ds1.add_attribute("type", "raw")
    ds1.add_attribute("annotated", "no")
    ds1.add_data_instances([ins5, ins6])
    ds2 = DataSet("D00000002_2023")
    ds2.add_attribute("type", "staging")
    ds2.add_attribute("annotated", "yes")
    ds2.add_data_instances([ins1, ins2])
    ds3 = DataSet("D00000003_2023_merge_output")
    ds3.add_data_instances([ins3, ins4])

    dop_merge = DataOperation("merge_op")
    dop_merge.add_attribute("code", "rc_merge")
    dop_merge.add_attribute("code_tag", "0_0_1")
    dop_merge.add_input([ds1, ds2])
    dop_merge.add_output([ds3])

    dop_preview = DataOperation("preview")
    dop_preview.add_attribute("code", "rc_preview")
    dop_preview.add_attribute("code_tag", "0_0_3")
    dop_preview.add_input([ds3])
    dop_preview.add_output([ds3])

    pipe = DataPipeline("test_pipe")
    pipe.add_attribute("version", "0_0_1")
    pipe.add_data_operations([dop_merge, dop_preview])

    ttl_file = tmp_path / "pipe.ttl"
    pipe.save_triplets_to_file(str(ttl_file))

    assert ttl_file.exists()
    assert (
        str(pipe.generate_triplets())
        == "['rc:0000001_png a rc:DataInstance ;\\n    rc:prefLabel \"0000001_png\"@en .\\n', 'rc:0000002_png a rc:DataInstance ;\\n    rc:prefLabel \"0000002_png\"@en .\\n', 'rc:0000003_png a rc:DataInstance ;\\n    rc:prefLabel \"0000003_png\"@en .\\n', 'rc:0000004_png a rc:DataInstance ;\\n    rc:prefLabel \"0000004_png\"@en .\\n', 'rc:0000005_png a rc:DataInstance ;\\n    rc:prefLabel \"0000005_png\"@en ;\\n    rc:hasAttributeValue rc:annotated_no .\\n', 'rc:0000006_png a rc:DataInstance ;\\n    rc:prefLabel \"0000006_png\"@en ;\\n    rc:hasAttributeValue rc:annotated_no .\\n', 'rc:D00000001_2023 a rc:DataSet ;\\n    rc:prefLabel \"D00000001_2023\"@en ;\\n    rc:containsData rc:0000005_png , rc:0000006_png ;\\n    rc:hasAttributeValue rc:type_raw , rc:annotated_no .\\n', 'rc:D00000002_2023 a rc:DataSet ;\\n    rc:prefLabel \"D00000002_2023\"@en ;\\n    rc:containsData rc:0000001_png , rc:0000002_png ;\\n    rc:hasAttributeValue rc:type_staging , rc:annotated_yes .\\n', 'rc:D00000003_2023_merge_output a rc:DataSet ;\\n    rc:prefLabel \"D00000003_2023_merge_output\"@en ;\\n    rc:containsData rc:0000003_png , rc:0000004_png .\\n', 'rc:annotated a rc:Attribute .\\nrc:no a rc:Value .\\nrc:annotated_no a rc:AttributeValue ;\\n    rc:hasAttribute rc:annotated ;\\n    rc:hasValue rc:no .\\n', 'rc:annotated a rc:Attribute .\\nrc:yes a rc:Value .\\nrc:annotated_yes a rc:AttributeValue ;\\n    rc:hasAttribute rc:annotated ;\\n    rc:hasValue rc:yes .\\n', 'rc:code a rc:Attribute .\\nrc:rc_merge a rc:Value .\\nrc:code_rc_merge a rc:AttributeValue ;\\n    rc:hasAttribute rc:code ;\\n    rc:hasValue rc:rc_merge .\\n', 'rc:code a rc:Attribute .\\nrc:rc_preview a rc:Value .\\nrc:code_rc_preview a rc:AttributeValue ;\\n    rc:hasAttribute rc:code ;\\n    rc:hasValue rc:rc_preview .\\n', 'rc:code_tag a rc:Attribute .\\nrc:0_0_1 a rc:Value .\\nrc:code_tag_0_0_1 a rc:AttributeValue ;\\n    rc:hasAttribute rc:code_tag ;\\n    rc:hasValue rc:0_0_1 .\\n', 'rc:code_tag a rc:Attribute .\\nrc:0_0_3 a rc:Value .\\nrc:code_tag_0_0_3 a rc:AttributeValue ;\\n    rc:hasAttribute rc:code_tag ;\\n    rc:hasValue rc:0_0_3 .\\n', 'rc:merge_op a rc:DataOperation ;\\n    rc:prefLabel \"merge_op\"@en ;\\n    rc:hasInput rc:D00000001_2023 , rc:D00000002_2023 ;\\n    rc:hasOutput rc:D00000003_2023_merge_output ;\\n    rc:hasAttributeValue rc:code_rc_merge , rc:code_tag_0_0_1 .\\n', 'rc:preview a rc:DataOperation ;\\n    rc:prefLabel \"preview\"@en ;\\n    rc:hasInput rc:D00000003_2023_merge_output ;\\n    rc:hasOutput rc:D00000003_2023_merge_output ;\\n    rc:hasAttributeValue rc:code_rc_preview , rc:code_tag_0_0_3 .\\n', 'rc:test_pipe a rc:DataPipeline ;\\n    rc:prefLabel \"test_pipe\"@en ;\\n    rc:consistsOf rc:merge_op , rc:preview ;\\n    rc:hasAttributeValue rc:version_0_0_1 .\\n', 'rc:type a rc:Attribute .\\nrc:raw a rc:Value .\\nrc:type_raw a rc:AttributeValue ;\\n    rc:hasAttribute rc:type ;\\n    rc:hasValue rc:raw .\\n', 'rc:type a rc:Attribute .\\nrc:staging a rc:Value .\\nrc:type_staging a rc:AttributeValue ;\\n    rc:hasAttribute rc:type ;\\n    rc:hasValue rc:staging .\\n', 'rc:version a rc:Attribute .\\nrc:0_0_1 a rc:Value .\\nrc:version_0_0_1 a rc:AttributeValue ;\\n    rc:hasAttribute rc:version ;\\n    rc:hasValue rc:0_0_1 .\\n']"  # noqa
    )
