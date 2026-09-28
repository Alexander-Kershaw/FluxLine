from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


"""
========================================================================================================

ELEXON FUELHH RECORD BASELMODEL:

========================================================================================================

The shape of the data returned by the ELEXON FUELHH API is as follows:

--------------------------------------------------------------------------------------------------------

{
    "data": [
        {...},
        {...}
    ]
}

--------------------------------------------------------------------------------------------------------

Therefore there are two structures returned by Elexon. 

One stucture is the response object, containing the list of records, and the other is the record object
itself, which contains the actual data.

I am modelling the record object here, which represents the actual data returned by the API.

The intention is the ElexonFuelHHResponse model will contain a list of ElexonFuelHHRecord objects,
under an ElexonFuelHHResponse.response attribute. This is so I have the following structure:

--------------------------------------------------------------------------------------------------------

FuelHHResponse
    │
    └── data
        │
        ├── FuelHHRecord
        ├── FuelHHRecord
        ├── FuelHHRecord
        └── ...

--------------------------------------------------------------------------------------------------------

I am modelling the external contract here, so the original source shape is being preserved faitherfully.

Also note, I have not been super explicity in defining the fields. e.g did not write:

fuel_type: Literal[
    "BIOMASS",
    "CCGT",
    ...
]

or 

settlement_period: int = Field(ge=1, le=48)

This is because the source data is not guaranteed to be static, changes happen, fuel types can be added,
settlement periods may differt from the normal 48 periods due to clock changes, etc
so I am being quite permissive in this model definition while designing it so changes to source data 
are caught early.

========================================================================================================
"""


class ElexonFuelHHRecord(BaseModel):

    model_config = ConfigDict(
        extra="forbid", # extra fields are forbidden, so changes to source data are caught early.
        strict=True # schema drift is possible, so being strict means changes to schema are caught early.
    )

    # Set to "FUELHH" for all records, so I dont end up with records from other datasets in the same list.
    dataset: Literal["FUELHH"] 

    # temporal fields are all strings in the source data, so I am preserving that datatype here.
    publish_time: str = Field(alias="publishTime")
    start_time: str = Field(alias="startTime")
    settlement_date: str = Field(alias="settlementDate")
    settlement_period: int = Field(alias="settlementPeriod")
    fuel_type: str = Field(alias="fuelType")

    generation: int



class ElexonFuelHHResponse(BaseModel):

    model_config = ConfigDict(
        extra="forbid",
        strict=True
    )

    data: list[ElexonFuelHHRecord] 


