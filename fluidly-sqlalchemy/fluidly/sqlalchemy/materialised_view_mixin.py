import sqlalchemy as db
from sqlalchemy import func


class MaterialisedViewMixin:
    view_generated_at = db.Column(
        db.DateTime, default=func.now(), server_default=func.now(), onupdate=func.now()
    )
