import io
from typing import Union

import pandas as pd
from fastapi import APIRouter, Depends, File, Form, UploadFile
from pandera.typing import DataFrame

from dnada import models, schemas
from dnada.api import deps

router = APIRouter()


@router.post("/validate", response_model=schemas.ValidationResponse)
async def standalone_validate_csv_schema(
    *,
    current_user: models.User = Depends(deps.get_current_active_user),
    csv: UploadFile = File(...),
    schema: str = Form(...),
) -> schemas.ValidationResponse:
    """
    Validate format of input csv using panderas
    """
    validation: schemas.ValidationResponse
    if schema not in schemas.VALIDATION_SCHEMAS:
        validation = schemas.ValidationResponse(
            ok=False,
            text=(
                f"{schema} not in possible schemas:"
                f" {str(schemas.VALIDATION_SCHEMAS.keys())}"
            ),
        )
    else:
        try:
            csv_contents: Union[str, bytes] = await csv.read()
            df: DataFrame = pd.read_csv(
                io.StringIO(
                    csv_contents.decode("utf-8")
                    if isinstance(csv_contents, bytes)
                    else csv_contents
                )
            )
            schemas.VALIDATION_SCHEMAS[schema].validate(df)
            validation = schemas.ValidationResponse(
                ok=True, text=f"Passed {schema} validation"
            )
        except Exception as err:
            validation = schemas.ValidationResponse(ok=False, text=str(err))
    return validation
