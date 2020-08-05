import sqlalchemy as db
from sqlalchemy import func


class TimestampMixin(object):
    last_seen_at = db.Column(
        db.DateTime, default=func.now(), server_default=func.now(), onupdate=func.now()
    )
    first_seen_at = db.Column(
        db.DateTime, default=func.now(), server_default=func.now()
    )
