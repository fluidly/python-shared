import sqlalchemy as db
from sqlalchemy import func


class UserActionMixin:
    # Creation
    created_at = db.Column(
        db.DateTime, default=func.now(), server_default=func.now(), nullable=False
    )
    created_by = db.Column(db.String)

    # Update
    updated_at = db.Column(
        db.DateTime,
        default=func.now(),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    updated_by = db.Column(db.String)

    # Deletion
    deleted_at = db.Column(db.DateTime)
    deleted_by = db.Column(db.String)
