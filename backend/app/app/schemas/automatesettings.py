from typing import Optional

from pydantic import BaseModel


# Shared properties
class AutomateSettingsBase(BaseModel):
    experiment_id: Optional[int] = None


# Properties to receive on item creation
class AutomateSettingsCreate(AutomateSettingsBase):
    experiment_id: int


# Properties to receive on item update
class AutomateSettingsUpdate(AutomateSettingsBase):
    pass


# Properties shared by models stored in DB
class AutomateSettingsInDBBase(AutomateSettingsBase):
    id: int
    experiment_id: int
    owner_id: int

    class Config:
        orm_mode = True


# Properties to return to client
class AutomateSettings(AutomateSettingsInDBBase):
    pass


# Properties properties stored in DB
class AutomateSettingsInDB(AutomateSettingsInDBBase):
    pass
