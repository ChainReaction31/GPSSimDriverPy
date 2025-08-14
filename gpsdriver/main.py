import math
import time

from consys4py.datamodels.api_utils import URI, UCUMCode
from consys4py.datamodels.swe_components import DataRecordSchema, TimeSchema, VectorSchema, QuantitySchema
from oshconnect.osh_connect_datamodels import Node
from oshconnect.osh_connect_datamodels import System
from oshconnect.oshconnectapi import OSHConnect
from oshconnect.timemanagement import TimeInstant


def main():
    osh = OSHConnect("GPSDriverConnect")
    local_node = Node("http", "localhost", 8282, "admin", "admin")

    osh.add_node(local_node)

    gps_system = System("GPSDriverSim", "GPS Driver Simulation", "urn:oshconnect:system:GPSDriverSim")

    osh.add_system(gps_system, local_node, True)

    datastream_schema = DataRecordSchema(label="GPS Simulated Location",
                                         description="GPS Simulated Location",
                                         definition="http://sensorml.com/ont/swe/property/Position", fields=[])
    timestamp = TimeSchema(label="Timestamp", name="timestamp", description="Timestamp of the GPS data",
                           definition="http://www.opengis.net/def/property/OGC/0/SamplingTime",
                           uom=URI(href="http://www.opengis.net/def/uom/ISO-8601/0/Gregorian"))

    location = VectorSchema(label="Location", name="location", description="GPS Location",
                            definition="http://www.opengis.net/def/property/OGC/0/SensorLocation",
                            reference_frame="http://www.opengis.net/def/crs/EPSG/0/4979",
                            coordinates=[QuantitySchema(label="Latitude", name="lat",
                                                        definition="http://sensorml.com/ont/swe/property/Latitude",
                                                        uom=UCUMCode(code='deg', label='degrees')),
                                         QuantitySchema(label="Longitude", name="lon",
                                                        definition="http://sensorml.com/ont/swe/property/Longitude",
                                                        uom=UCUMCode(code='deg', label='degrees')),
                                         QuantitySchema(label="Altitude", name="alt",
                                                        definition="http://sensorml.com/ont/swe/property/Altitude",
                                                        uom=UCUMCode(code='m', label='meters'))])

    orientation = QuantitySchema(label="Orientation", name="orientation", description="GPS Orientation - Heading",
                                 definition="http://sensorml.com/ont/swe/property/Orientation",
                                 uom=UCUMCode(code='deg', label='degrees'))
    datastream_schema.fields.append(timestamp)
    datastream_schema.fields.append(location)
    datastream_schema.fields.append(orientation)

    datastream = gps_system.add_insert_datastream(datastream_schema)

    # Set base coordinates around Huntsville, AL
    # My math is rusty, but I believe this may always appear to be a circle, however, I think that the points won't
    # actually be equidistant around the poles
    base_lat = 34.7304  # Huntsville latitude
    base_lon = -86.5861  # Huntsville longitude
    base_alt = 200.0  # Example: base altitude in meters for Huntsville
    radius_deg = 0.003  # ~111m per 0.001 deg latitude
    alt_variation = 10.0  # Altitude varies +/-10m
    angle = 0.0
    angle_step = math.radians(5)  # 5 degree step per iteration

    while True:
        timeinstant = TimeInstant.now_as_time_instant()
        timedata = timeinstant.get_iso_time()
        # Calculate point on circle
        lat = base_lat + radius_deg * math.cos(angle)
        lon = base_lon + radius_deg * math.sin(angle)
        alt = base_alt + alt_variation * math.sin(angle)
        angle += angle_step

        gps_sim_data = {
            "resultTime": timedata,
            "phenomenonTime": timedata,
            "result": {
                # "timestamp": timeinstant.epoch_time,
                "location": {
                    "lat": lat,
                    "lon": lon,
                    "alt": alt
                },
                "orientation": 180.0
            }
        }

        datastream.insert_observation_dict(gps_sim_data)
        time.sleep(2)  # Wait 2 seconds before next iteration


main()
