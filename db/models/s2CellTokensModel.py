from app import db, app


class S2CellTokens(db.Model):
    __tablename__ = 's2_cell_tokens'

    id = db.Column(db.Integer, primary_key=True)
    cell_token = db.Column(db.String(), unique=True)
    cell_geo_ids = db.relationship('CellsGeosMiddle', backref='s2_cell_tokens')

    def __init__(self, cell_token):
        self.cell_token = cell_token

    def __repr__(self):
        return '<id {}>'.format(self.id)
