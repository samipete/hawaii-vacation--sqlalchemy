import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

 # Create our session (link) from Python to the DB
session = Session(engine)
#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

# homepage
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )


# route to precipitation
@app.route("/api/v1.0/precipitation")
# define a function that converts the precipitation analysis (ie the last 12 months)
def prcp():
    session = Session(engine)

   # find one year ago from most recent date in data set
    one_yr_back = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    # query
    preci_data = session.query(Measurement.date, Measurement.prcp).\
    filter (Measurement.date >= one_yr_back).\
    order_by (Measurement.date).all()
    # return as jsonified dictionary  
    all_prcp = []
    for date, prcp in preci_data:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp

        all_prcp.append(prcp_dict)
        
    session.close()

    return jsonify(all_prcp)

# route for stations 
@app.route("/api/v1.0/stations")
 # define a function that will show all stations and return jsonified list
def stations():
    session = Session(engine)

    all_stations=session.query(Station.station).all()
    lst_stations = list(np.ravel(all_stations))
    
    session.close()

    return jsonify(lst_stations)

# route for tobs (temperature observations)
@app.route("/api/v1.0/tobs")
def temp_obs():
    session = Session(engine)

    # identify previous year obsevations 
    mst_rct_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    mst_rct_date = dt.datetime.strptime(mst_rct_date, '%Y-%m-%d')
    query_dt = dt.date(mst_rct_date.year -1, mst_rct_date.month, mst_rct_date.day)    
    
    # use the query dt variable to find the tobs for the most active station 
    temp_obs=session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.station == 'USC00519281').\
    filter(Measurement.date >=query_dt).all()

    # return tobs as jsonified list
    all_tobs = []
    for date, tobs in temp_obs:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs

        all_tobs.append(tobs_dict)
        
    session.close()

    return jsonify(all_tobs)

# route for start
@app.route("/api/v1.0/<start>")
def start_tobs(start):
    session = Session(engine)

    # write the function and query that allows the user to input a dynamic start date (return in json format)
    start_date = dt.datetime.strptime(start, "%Y%m%d")
    # find the min max and avg temperatures from the specified start date
    temp_obs=session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start_date) \
        .all()
    lst_tobs = list(np.ravel(temp_obs))
    
    session.close()

    return jsonify(lst_tobs)

# start/end
@app.route("/api/v1.0/<start>/<end>")
# define a function that will allow user to set a specific start and end date
def st_end_tobs(start, end):
    session = Session(engine)

    start_date = dt.datetime.strptime(start, "%Y%m%d")
    end_date = dt.datetime.strptime(end, "%Y%m%d")

    # query the min max and average temp for the identified start/end date and return as jsonified list
    temp_obs=session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start_date).\
        filter(Measurement.date <= end_date).all()
    
    lst_tobs = list(np.ravel(temp_obs))
    
    session.close()

    return jsonify(lst_tobs)
    

if __name__ == '__main__':
    app.run(debug=True)
