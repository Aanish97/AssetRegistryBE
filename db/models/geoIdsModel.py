from app import db, app


class GeoIds(db.Model):
    __tablename__ = 'geo_ids'

    geo_id = db.Column(db.Integer, primary_key=True)
    cell_id = db.Column(db.String(), db.ForeignKey('s2_cell_tokens.cell_id'), nullable=False)

    def __init__(self, cell_id):
        self.cell_id = cell_id

    def __repr__(self):
        return '<geo_id {}>'.format(self.geo_id)
