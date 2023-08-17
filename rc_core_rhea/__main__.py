import logging
import os
import platform
import random
import shutil
from typing import Any, Final, Optional, Tuple, Union

import typer
from rich.console import Console, ConsoleDimensions
from rich.layout import Layout
from rich.panel import Panel
from rich.prompt import Prompt
from rich.style import Style
from rich.tree import Tree

from rc_core_rhea import DataOperation, DataPipeline, DataSet, ProvenanceComponent

logging.disable(logging.CRITICAL + 1)
logger: Final[logging.Logger] = logging.getLogger("rc-rhea")

app = typer.Typer(no_args_is_help=True)


console = Console()


@app.command(help="Creating provenace file in RDF.", no_args_is_help=True)
def create(
    provenance_file: str = typer.Option(
        None,
        "-o",
        "--output",
        help="Output path to provenand file in .ttl format.",
    )) -> None:

    clear_terminal()
    with console.screen() as screen:
        provenance: ProvenanceComponent = display_wizard(provenance_file, screen)  # type:ignore
        provenance.save_triplets_to_file(str(provenance_file))

    console.print(
        f"\n>> Provenance saved successfully! <<\n{provenance_file}\n", style=Style.parse("navy_blue on white bold"), justify="center"
    )


def display_wizard(
    provenance_file: Union[str, None, ProvenanceComponent],
    screen: Any,
) -> None:
    layout = Layout(name="tree")

    random_id = "".join(random.choices("0123456789", k=5))
    pipe_id = f"pipe_{random_id}"
    tree = Tree(pipe_id)
    pipe = None

    clear_terminal()
    _width, _height = shutil.get_terminal_size()
    console.size = ConsoleDimensions(_width - 1, _height - 10)

    console.print(
        "PROVENANCE GENERATOR - Rhea Project",
        justify="center",
        style=Style.parse("navy_blue on white bold"),
    )

    layout["tree"].update(Panel(tree))
    screen.update(layout)

    pipe, tree = display_provenance_dialog(pipe_id, layout, screen)

    return pipe


def display_provenance_dialog(pipe_id: str, layout: Layout, screen: Any) -> Tuple[ProvenanceComponent, Tree]:
    """
    Provenance creation
    [1]  Create Dataset
    [2]  Create DataOperation
    [3]  Refresh terminal
    [4]  Finish
    """
    refresh_layout(screen, layout)

    pipe = DataPipeline(pipe_id)
    datasets: list[DataSet] = []
    dataset_names: list[str] = []
    dataops: list[DataOperation] = []
    dataop_names: list[str] = []
    cli_tree: Tree = Tree(f"[navy_blue on white bold] {pipe_id} ")

    selected_option = ""
    while selected_option != "0":
        options = [
            ":one:  Create Dataset",
            ":two:  Create DataOperation",
            ":three:  Refresh terminal",
            ":zero:  Save & Exit",
            "",
        ]
        console.print("\n[navy_blue on white bold]Provenance creation[/]")
        selected_option = Prompt.ask(
            "\n".join([option for option in options]), choices=["1", "2", "3", "0"], default="1"
        )

        if selected_option != "":
            layout["tree"].update(Panel(cli_tree))

        refresh_layout(screen, layout)

        if selected_option == "1":
            new_ds = display_dataset_creation_dialog(datasets)
            datasets.append(new_ds)
            dataset_names.append(new_ds.name)

        refresh_layout(screen, layout)

        if selected_option == "2":
            if len(datasets) < 1:
                Prompt.ask("[dark_red] At least one dataset needs to be created.", default="Enter to continue...")
            else:
                new_dop = display_dataop_creation_dialog(datasets, dataset_names, dataops, screen, layout)
                dataops.append(new_dop)
                dataop_names.append(new_dop.name)
                cli_tree.add(new_dop.generate_cli_tree())
                layout["tree"].update(Panel(cli_tree))

        refresh_layout(screen, layout)

    pipe.add_data_operations(dataops)

    return pipe, cli_tree


def display_dataset_creation_dialog(datasets: list[DataSet]) -> DataSet:
    if len(datasets) > 0:
        console.print("\n[bright_blue]Displaying current datasets...")
        for ds in datasets:
            console.print(ds.generate_cli_tree())
    console.print("\n[navy_blue on white bold]Create new dataset")
    name = Prompt.ask("[bold]Dataset name?")
    new_ds = DataSet(name)

    choice = ""
    while choice != "Exit":
        add_att = Prompt.ask("[bold]Add attribute?", choices=["yes", "no"], default="yes")
        if add_att == "yes":
            att_name = Prompt.ask(" [bold]Attribute name")
            att_value = Prompt.ask(" [bold]Attribute value")
            new_ds.add_attribute(att_name, att_value)
        else:
            choice = "Exit"

    return new_ds


def display_dataop_creation_dialog(
    datasets: list[DataSet],
    dataset_names: list[str],
    dataops: list[DataOperation],
    screen: Any,
    layout: Layout,
) -> DataOperation:
    refresh_layout(screen, layout)

    if len(dataops) > 0:
        console.print("[bright_blue]Displaying current DataOps...")
        for dop in dataops:
            console.print(dop.generate_cli_tree())

    console.print("\n[navy_blue on white bold]Create new DataOp")
    name = Prompt.ask("[bold]DataOp name?")
    new_dop = DataOperation(name)

    choice = ""
    while choice != "Exit":
        add_att = Prompt.ask("[bold]Add attribute?", choices=["yes", "no"], default="yes")
        if add_att == "yes":
            att_name = Prompt.ask("[bold]Attribute name")
            att_value = Prompt.ask("[bold]Attribute value")
            new_dop.add_attribute(att_name, att_value)
        else:
            choice = "Exit"

    if len(datasets) > 0:
        console.print("\n[bright_blue]Displaying current DataSets...")
        for ds in datasets:
            console.print(ds.generate_cli_tree())

    add_in_ds = Prompt.ask("\n[bold]Add input Dataset?", choices=["yes", "no"], default="yes")
    if add_in_ds == "yes":
        ds_name = Prompt.ask("[bold]Input Dataset name", choices=dataset_names)
        for ds in datasets:
            if ds.name == ds_name:
                new_dop.add_input([ds])
                break

    add_out_ds = Prompt.ask("[bold]Add output Dataset?", choices=["yes", "no"], default="yes")
    if add_out_ds == "yes":
        ds_name = Prompt.ask("[bold]Output Dataset name", choices=dataset_names)
        for ds in datasets:
            if ds.name == ds_name:
                new_dop.add_output([ds])
                break

    return new_dop


def refresh_layout(screen: Any, layout: Layout) -> None:
    _width, _height = shutil.get_terminal_size()
    console.size = ConsoleDimensions(_width - 1, _height - 10)
    clear_terminal()
    main_title_style = Style.parse("navy_blue on white bold")
    console.print("PROVENANCE GENERATOR - Rhea Project", justify="center", style=main_title_style)
    screen.update(layout)


def clear_terminal() -> None:
    """Clear the terminal screen."""
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")


if __name__ == "__main__":
    app()
