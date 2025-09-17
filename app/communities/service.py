import logging
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlmodel import Session, select

from app.communities.models import Community, CommunityCreate, CommunityUpdate

logger = logging.getLogger(__name__)


def create_community(
    *, session: Session, community_create: CommunityCreate, created_by: UUID
) -> Community:
    """Create a new community."""
    db_obj = Community.model_validate(
        community_create, update={"created_by": created_by}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    logger.info(f"Created community: {db_obj.id}")
    return db_obj


def get_community(*, session: Session, community_id: UUID) -> Optional[Community]:
    """Get a community by ID."""
    statement = select(Community).where(Community.id == community_id)
    community = session.exec(statement).first()
    logger.info(f"Retrieved community: {community}")
    return community


def get_communities(
    *,
    session: Session,
    skip: int = 0,
    limit: int = 100,
    is_public: Optional[bool] = None,
    is_active: Optional[bool] = None,
) -> List[Community]:
    """Get communities with optional filtering."""
    statement = select(Community)

    if is_public is not None:
        statement = statement.where(Community.is_public == is_public)

    if is_active is not None:
        statement = statement.where(Community.is_active == is_active)

    statement = statement.offset(skip).limit(limit)
    communities = session.exec(statement).all()
    logger.info(f"Retrieved {len(communities)} communities")
    return communities


def get_communities_by_creator(
    *, session: Session, created_by: UUID, skip: int = 0, limit: int = 100
) -> List[Community]:
    """Get communities created by a specific user."""
    statement = select(Community).where(Community.created_by == created_by)
    statement = statement.offset(skip).limit(limit)
    communities = session.exec(statement).all()
    logger.info(f"Retrieved {len(communities)} communities for user {created_by}")
    return communities


def update_community(
    *, session: Session, db_community: Community, community_in: CommunityUpdate
) -> Community:
    """Update a community."""
    community_data = community_in.model_dump(exclude_unset=True)
    community_data["updated_at"] = datetime.utcnow()

    db_community.sqlmodel_update(community_data)
    session.add(db_community)
    session.commit()
    session.refresh(db_community)
    logger.info(f"Updated community: {db_community.id}")
    return db_community


def delete_community(*, session: Session, community_id: UUID) -> bool:
    """Delete a community (soft delete by setting is_active=False)."""
    community = get_community(session=session, community_id=community_id)
    if not community:
        return False

    community.is_active = False
    community.updated_at = datetime.utcnow()
    session.add(community)
    session.commit()
    logger.info(f"Soft deleted community: {community_id}")
    return True


def hard_delete_community(*, session: Session, community_id: UUID) -> bool:
    """Permanently delete a community from the database."""
    community = get_community(session=session, community_id=community_id)
    if not community:
        return False

    session.delete(community)
    session.commit()
    logger.info(f"Hard deleted community: {community_id}")
    return True


def search_communities(
    *, session: Session, query: str, skip: int = 0, limit: int = 100
) -> List[Community]:
    """Search communities by name or description."""
    statement = select(Community).where(
        (Community.name.ilike(f"%{query}%"))
        | (Community.description.ilike(f"%{query}%"))
    )
    statement = statement.offset(skip).limit(limit)
    communities = session.exec(statement).all()
    logger.info(f"Found {len(communities)} communities matching query: {query}")
    return communities
