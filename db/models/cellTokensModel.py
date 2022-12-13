from app import db, app


class S2CellTokens(db.Model):
    __tablename__ = 's2_cell_tokens'

    id = db.Column(db.Integer, primary_key=True)
    cell_id = db.Column(db.String(), unique=True, primary_key=True)
    cells = db.relationship("S2CellTokens", backref="cells")
    resolution_level = db.Column(db.Integer())

    def __init__(self, cell_id, resolution_level):
        self.cell_id = cell_id
        self.resolution_level = resolution_level

    def __repr__(self):
        return '<id {}>'.format(self.id)
