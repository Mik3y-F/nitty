import logging
from typing import Annotated, Any, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer

import app.communities.service as community_service
from app.auth.models import User
from app.communities.models import CommunityCreate, CommunityPublic, CommunityUpdate
from app.database import DbSession
from app.deps import get_current_user

logger = logging.getLogger(__name__)

communities_router = APIRouter(tags=["communities"])
security = HTTPBearer()


@communities_router.post("/", response_model=CommunityPublic)
def create_community(
    session: DbSession,
    community_in: CommunityCreate,
    current_user: Annotated[User, Depends(get_current_user)],
) -> Any:
    """Create a new community."""
    community = community_service.create_community(
        session=session, community_create=community_in, created_by=current_user.id
    )
    return community


@communities_router.get("/", response_model=List[CommunityPublic])
def get_communities(
    session: DbSession,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_public: Optional[bool] = Query(None),
    is_active: Optional[bool] = Query(None),
) -> Any:
    """Get communities with optional filtering."""
    communities = community_service.get_communities(
        session=session,
        skip=skip,
        limit=limit,
        is_public=is_public,
        is_active=is_active,
    )
    return communities


@communities_router.get("/search", response_model=List[CommunityPublic])
def search_communities(
    session: DbSession,
    q: str = Query(..., min_length=1, max_length=100),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> Any:
    """Search communities by name or description."""
    communities = community_service.search_communities(
        session=session, query=q, skip=skip, limit=limit
    )
    return communities


@communities_router.get("/my", response_model=List[CommunityPublic])
def get_my_communities(
    session: DbSession,
    current_user: Annotated[User, Depends(get_current_user)],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> Any:
    """Get communities created by the current user."""
    communities = community_service.get_communities_by_creator(
        session=session, created_by=current_user.id, skip=skip, limit=limit
    )
    return communities


@communities_router.get("/{community_id}", response_model=CommunityPublic)
def get_community(
    session: DbSession,
    community_id: UUID,
) -> Any:
    """Get a specific community by ID."""
    community = community_service.get_community(
        session=session, community_id=community_id
    )
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")
    return community


@communities_router.put("/{community_id}", response_model=CommunityPublic)
def update_community(
    session: DbSession,
    community_id: UUID,
    community_in: CommunityUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
) -> Any:
    """Update a community."""
    community = community_service.get_community(
        session=session, community_id=community_id
    )
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")

    # Check if user is the creator
    if community.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    community = community_service.update_community(
        session=session, db_community=community, community_in=community_in
    )
    return community


@communities_router.delete("/{community_id}")
def delete_community(
    session: DbSession,
    community_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
) -> Any:
    """Delete a community (soft delete)."""
    community = community_service.get_community(
        session=session, community_id=community_id
    )
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")

    # Check if user is the creator
    if community.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    success = community_service.delete_community(
        session=session, community_id=community_id
    )
    if not success:
        raise HTTPException(status_code=400, detail="Failed to delete community")

    return {"message": "Community deleted successfully"}


@communities_router.delete("/{community_id}/permanent")
def permanently_delete_community(
    session: DbSession,
    community_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
) -> Any:
    """Permanently delete a community from the database."""
    community = community_service.get_community(
        session=session, community_id=community_id
    )
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")

    # Check if user is the creator
    if community.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    success = community_service.hard_delete_community(
        session=session, community_id=community_id
    )
    if not success:
        raise HTTPException(
            status_code=400, detail="Failed to permanently delete community"
        )

    return {"message": "Community permanently deleted"}
