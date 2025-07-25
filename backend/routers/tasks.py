
from fastapi import APIRouter, Depends
from models.tasks import ProactiveAnalysisRequest
from models.user import User
from core.auth import get_current_user
from services.aegnt_service import AegntService

router = APIRouter()

aegnt_service = AegntService()

@router.post("/tasks/proactive_analysis")
def trigger_proactive_analysis(request: ProactiveAnalysisRequest, current_user: User = Depends(get_current_user)):
    """
    An endpoint designed to be called by a scheduler.
    """
    aegnt_service.trigger_proactive_analysis(request.user_id)
    return {"status": "success", "message": f"Proactive analysis triggered for user {request.user_id}"}
