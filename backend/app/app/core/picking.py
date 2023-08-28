import typing as t
from pandera.typing import DataFrame
import pandera as pa

from app import schemas


def well_generator() -> t.Generator[str, None, None]:
    for col in range(1, 13):
        for row in "ABCDEFGH":
            yield f"{row}{col}"


@pa.check_types
def create_picking_instructions(
    plating_instructions: DataFrame[schemas.PlatingInstructionsSchema],
    n_colonies_per_construct: int = 3,
) -> DataFrame[schemas.PickingResultsSchema]:
    """Generate picking worksheet assuming transformation for each construct
    was successful
    """
    # Initialize the well generator and plate counter
    wells = well_generator()
    plate_counter: int = 1

    # List to hold data for the new dataframe
    data: list[dict[str, str]] = []

    # Iterate over each row in the given dataframe
    for _, row in plating_instructions.iterrows():
        for _ in range(n_colonies_per_construct):
            try:
                # Get next available well
                dest_well = next(wells)
            except StopIteration:
                # If we run out of wells, reset the generator and increment
                # the plate_counter
                wells = well_generator()
                plate_counter += 1
                dest_well = next(wells)

            data.append(
                {
                    "Source Barcode": row["QPLATE"],
                    "Source Region": row["QWELL"],
                    "Destination Barcode": f"glycerol_plate_{plate_counter}",
                    "Destination Well": dest_well,
                }
            )

    return DataFrame(data)
