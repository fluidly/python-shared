import sqlalchemy as db

class MockModel:
    __tablename__ = "mock_model"
    id = db.Column(db.String, primary_key=True)

    connection_id = db.Column(db.String, nullable=False, index=True)

    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, nullable=False)

    counterparty_id = db.Column(db.String, index=True)
    currency_code = db.Column(db.String)
    description = db.Column(db.String)
    raised_date = db.Column(db.Date)