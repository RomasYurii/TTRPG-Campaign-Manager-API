from fastapi import APIRouter, HTTPException,status, Depends
from database import schemas
from database.database import get_db, Session
from database import models
from security import get_current_user

router = APIRouter()


@router.post("/campaigns", status_code=status.HTTP_201_CREATED)
def create_campaign(campaign: schemas.CampaignCreate, current_user: models.User = Depends(get_current_user) ,db: Session = Depends(get_db)):

    if current_user.role != "dm":
        raise HTTPException(status_code=403, detail="Only Dungeon Masters can create campaigns")


    new_campaign = models.Campaign(
        title=campaign.title,
        description=campaign.description,
        dm_id=current_user.id,
    )

    db.add(new_campaign)
    db.commit()
    db.refresh(new_campaign)


    return {"message": "Campaign created successfully", "Campaign": campaign.title}


@router.get("/campaigns")
def list_campaigns( current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role == "dm":
        return db.query(models.Campaign).filter(models.Campaign.dm_id == current_user.id).all()
    else:
        return []