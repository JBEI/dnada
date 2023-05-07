from app.crud.base import CRUDBaseExperiment
from app.models.resultzip import ResultZip
from app.schemas.resultzip import ResultZipCreate, ResultZipUpdate


class CRUDResultZip(
    CRUDBaseExperiment[ResultZip, ResultZipCreate, ResultZipUpdate]
):

    """CRUD Methods for ResultZips"""


resultzip = CRUDResultZip(ResultZip)
