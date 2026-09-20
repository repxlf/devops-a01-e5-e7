from enum import Enum


class Stage(str, Enum):
    DRAFT = "DRAFT"
    FULL_CHECK = "FULL_CHECK"
    INCREMENTAL_CHECK = "INCREMENTAL_CHECK"
    REPAIR = "REPAIR"
    RECHECK = "RECHECK"
