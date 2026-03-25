from pydantic import BaseModel


class LegacyPayload(BaseModel):
    message: str = "Legacy v1 payloads are not supported by default"
