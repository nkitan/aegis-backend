
from pydantic import BaseModel

class ProactiveAnalysisRequest(BaseModel):
    user_id: str
