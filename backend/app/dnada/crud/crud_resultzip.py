from dnada.crud.base import CRUDBaseExperiment
from dnada.models.resultzip import ResultZip
from dnada.schemas.resultzip import ResultZipCreate, ResultZipUpdate


class CRUDResultZip(CRUDBaseExperiment[ResultZip, ResultZipCreate, ResultZipUpdate]):

    """CRUD Methods for ResultZips"""


resultzip = CRUDResultZip(ResultZip)
