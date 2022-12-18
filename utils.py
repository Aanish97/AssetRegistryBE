import json
import hashlib

from app import db
from db.models.geoIdsModel import GeoIds
from db.models.cellsGeosMiddleModel import CellsGeosMiddle
from db.models.s2CellTokensModel import S2CellTokens


class Utils:
    """
    Utils class for helper functions
    """

    @staticmethod
    def populate_new_s2_cell_tokens(s2_cell_tokens: list):
        all_saved_s2_cell_tokens = S2CellTokens.query.filter(S2CellTokens.cell_token.in_(set(s2_cell_tokens)))
        all_saved_s2_cell_tokens = [r.cell_token for r in all_saved_s2_cell_tokens]
        to_add_s2_cell_tokens = list(set(s2_cell_tokens) - set(all_saved_s2_cell_tokens))
        records_list_s2_cell_tokens = []
        for to_add_s2_cell_token in to_add_s2_cell_tokens:
            records_list_s2_cell_tokens.append(S2CellTokens(cell_token=to_add_s2_cell_token))
        db.session.add_all(records_list_s2_cell_tokens)
        db.session.commit()

    @staticmethod
    def generate_geo_id(s2_cell_tokens):
        """
        each list of `s2_index__L20_list` will always have a unique GEO_ID
        """
        s2_tuple = tuple(s2_cell_tokens)
        m = hashlib.sha256()

        # encoding the s2 tokens list
        for s in s2_tuple:
            m.update(s.encode())
        geo_id = m.hexdigest()  # <-- geoid

        # order matters
        return geo_id

    @staticmethod
    def lookup_geo_ids(geo_id_to_lookup):
        """
        check if the geo id (field boundary) is already registered
        """
        exists = db.session.query(GeoIds.id).filter_by(geo_id=geo_id_to_lookup).first() is not None
        return exists

    @staticmethod
    def register_field_boundary(geo_id, s2_cell_tokens, resolution_level):
        """
        registering the geo id (field boundary) in the database
        """
        geo_data = json.dumps({'s2_L' + str(resolution_level): s2_cell_tokens})
        geo_id_record = GeoIds(geo_id, geo_data)
        db.session.add(geo_id_record)
        db.session.commit()
        return

    @staticmethod
    def fetch_geo_ids_for_cell_tokens(s2_cell_tokens, resolution_level):
        """
        fetch the geo ids which at least one token from the tokens list given
        """
        cell_ids = db.session.query(S2CellTokens).filter(S2CellTokens.cell_token.in_(s2_cell_tokens)).all()
        return cell_ids
