import sqlalchemy as db


class UserActionMixin(object):
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)
    created_by = db.Column(db.Integer)
    updated_by = db.Column(db.Integer)
    deleted_at = db.Column(db.DateTime)
