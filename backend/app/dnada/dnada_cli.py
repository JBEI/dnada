import typer
from pathlib import Path
from fastapi import UploadFile
from dnada.core.process_design import process_j5_zip_upload
from dnada.core.condense_designs import condense_designs
from dnada.core.j5_to_echo import j5_to_echo
from dnada.core import j5


cli = typer.Typer()


@cli.command()
def condense_and_automate_j5(
    files: list[Path],
    output: Path = typer.Option(
        "automation_instructions.zip", help="Path to save the output file."
    ),
) -> None:
    """Condense j5 design zip files into single design then create
    customized automation instructions for J5 Design."""
    designs: list[j5.J5Design] = []
    for file in files:
        with file.open("rb") as f:
            designs.append(process_j5_zip_upload(UploadFile(f, filename=file.name)))
    condensed = condense_designs(designs)
    _, result = j5_to_echo(j5_design=condensed)
    result.seek(0)
    with output.open("wb") as out_file:
        out_file.write(result.read())
    typer.echo(f"Output saved to {output}")


if __name__ == "__main__":
    cli()
