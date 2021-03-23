import sqlalchemy as db


class TimestampMixin(object):
    last_seen_at = db.Column(db.DateTime)
    first_seen_at = db.Column(db.DateTime)
