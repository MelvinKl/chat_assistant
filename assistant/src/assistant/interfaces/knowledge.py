from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class Knowledge:
    def __init__(
        self,
        information: str,
        uuid: Optional[UUID] = None,
        expiration_date: Optional[datetime] = None,
    ):
        self.uuid = uuid if uuid is not None else uuid4()
        self.information = information
        self.expiration_date = expiration_date
