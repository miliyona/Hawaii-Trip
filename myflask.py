
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
from sqlalchemy import inspect
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy

def connect_reflect():
    engine = create_engine(
          "sqlite:///Resources/hawaii.sqlite")

    session = Session(engine)
    Base = automap_base()
    Base.prepare(engine, reflect=True)
    inspector = inspect(engine)
    return Base, inspector, session, engine
schema, inspector, session,engine = connect_reflect()
schema.classes.items()
Measurement = schema.classes.measurement
Station = schema.classes.station


app = Flask(__name__)

@app.route("/")
def Home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"- List of prior year rain totals from all stations<br/>"
        f"<br/>"
        f"/api/v1.0/stations<br/>"
        f"- List of Station numbers and names<br/>"
        f"<br/>"
        f"/api/v1.0/tobs<br/>"
        f"- List of prior year temperatures from all stations<br/>"
        f"<br/>"
        f"/api/v1.0/start<br/>"
        f"- When given the start date (YYYY-MM-DD), calculates the MIN/AVG/MAX temperature for all dates greater than and equal to the start date<br/>"
        f"<br/>"
        f"/api/v1.0/start/end<br/>"
        f"- When given the start and the end date (YYYY-MM-DD), calculate the MIN/AVG/MAX temperature for dates between the start and end date inclusive<br/>"

    )
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

@app.route("/api/v1.0/precipitation")
def precipitation():
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_year = dt.date(2017, 8, 5) - dt.timedelta(days=365)
    temp_prcp = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date > last_year).\
        order_by(Measurement.date).all()

# Creating a dicts from the above query.
    temp_dict = []
    for temp in temp_prcp:
        row = {}
        row["date"] = temp_prcp[0][0]
        row["tobs"] = temp_prcp[1][1]
        temp_dict.append(row)
        return jsonify(temp_dict)

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

@app.route("/api/v1.0/stations")
def stations():
    stations = session.query(Station.name, Station.station,Station.latitude,Station.longitude,Station.elevation)
    stations_df = pd.read_sql(stations.statement, stations.session.bind)
    return jsonify(stations_df.to_dict())

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

@app.route("/api/v1.0/tobs")
def tobs():
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_year = dt.date(2017, 8, 5) - dt.timedelta(days=365)
    temp_last_year = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date > last_year).\
        order_by(Measurement.date).all()

    temperature = []
    for temp in temp_last_year:
        row = {}
        row["date"] = temp_last_year[0][0]
        row["tobs"] = temp_last_year[1][1]
        temperature.append(row)
    return jsonify(temperature)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@app.route("/api/v1.0/<start>")
def trip1(start):
    start_date= dt.datetime.strptime(start, '%Y-%m-%d')
    last_year = dt.timedelta(days=365)
    start = start_date-last_year
    end =  dt.date(2017, 8, 23)
    trip_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    trip = list(np.ravel(trip_data))
    return jsonify(trip)

#########################################################################################
@app.route("/api/v1.0/<start>/<end>")
def trip2(start,end):

  # go back one year from start/end date and get Min/Avg/Max temp     
    start_date= dt.datetime.strptime(start, '%Y-%m-%d')
    end_date= dt.datetime.strptime(end,'%Y-%m-%d')
    last_year = dt.timedelta(days=365)
    start = start_date-last_year
    end = end_date-last_year
    trip_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    trip = list(np.ravel(trip_data))
    return jsonify(trip)

#########################################################################################

if __name__ == "__main__":
    app.run(debug=True)