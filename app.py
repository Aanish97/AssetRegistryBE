import os
import json
import hashlib
import fiona
import geopandas as gpd
from flask import Flask, jsonify, request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from shapely.wkt import loads
import s2sphere as s2

from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config.from_object(os.getenv('APP_SETTINGS'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
from db.models import geoIdsModel, s2CellTokensModel, cellsGeosMiddleModel

migrate = Migrate(app, db)


@app.route('/generate-geo-id', methods=['POST'])
def generate_geo_ids():
    """
    each list of `s2_index__L20_list` will always have a unique GEO_ID
    """

    data = json.loads(request.data.decode('utf-8'))
    s2_tokens = data.get('s2_tokens')

    s2_tuple = tuple(s2_tokens)
    m = hashlib.sha256()

    # encoding the s2 tokens list
    for s in s2_tuple:
        m.update(s.encode())
    geo_id = m.hexdigest()  # <-- geoid

    # order matters
    return jsonify({
        "GEO ID": geo_id
    })


@app.route('/wkt-to-cell-ids', methods=['POST'])
def wkt_to_cell_ids():
    data = json.loads(request.data.decode('utf-8'))
    field_wkt = data.get('wkt')
    res_level = data.get('level')

    poly = loads(field_wkt)

    longs, lats = poly.exterior.coords.xy
    longs, lats = longs.tolist(), lats.tolist()

    min_level = res_level
    max_level = res_level
    r = s2.RegionCoverer()
    r.min_level = min_level
    r.max_level = max_level

    lb_lat = min(lats)
    ub_lat = max(lats)
    lb_lon = min(longs)
    ub_lon = max(longs)

    lb = s2.LatLng.from_degrees(lb_lat, lb_lon)
    ub = s2.LatLng.from_degrees(ub_lat, ub_lon)
    cids = r.get_covering(s2.LatLngRect.from_point_pair(lb, ub))
    s2_token_list = []
    for cid in cids:
        s2_token_list.append(cid.to_token())

    return jsonify({
        "s2 token list": s2_token_list,
    })


@app.route('/kml-to-wkt', methods=['POST'])
def convert_kml_to_wkt():
    kml_file = request.files.get('kml')

    fiona.supported_drivers['KML'] = 'rw'
    f = fiona.BytesCollection(bytes(kml_file.content))
    df = gpd.GeoDataFrame()

    gdf = gpd.read_file(kml_file, driver='KML')
    poly = gdf.geometry.iloc[0]  # shapely polygon
    wkt = poly.wkt


if __name__ == '__main__':
    app.run()
