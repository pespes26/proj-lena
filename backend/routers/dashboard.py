from fastapi import APIRouter, HTTPException, Depends
from services.unified import load_unified_dashboard
from auth import get_current_user

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("/api/dashboard")
def get_dashboard():
    try:
        return {"data": load_unified_dashboard()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"שגיאה בטעינת נתוני דשבורד: {str(e)}")
