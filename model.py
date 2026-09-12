import pandas as pd
import numpy as np


class Result:
    def init(self):
        self.best_route = None
        self.acd_time = None
        self.acd_time_lower = None
        self.acd_time_upper = None
        self.ace_time = None
        self.ace_time_lower = None
        self.ace_time_upper = None
        self.bcd_time = None
        self.bcd_time_lower = None
        self.bcd_time_upper = None
        self.bce_time = None
        self.bce_time_lower = None
        self.bce_time_upper = None


def pred_acd(x):
    amplitude = 33.52533001
    angular_frequency = 4.79692269
    phase_offset = 2.31996204
    vertical_offset = 105.43875151
    return amplitude * np.sin(angular_frequency * x + phase_offset) + vertical_offset

def pred_ace(x):
    slope = 1.07686462
    vertical_offset = 97.16703124
    return slope * x + vertical_offset
    
def pred_bcd(x):
    vertical_offset = 1.40993318e+02
    amplitude = 3.26487772e+01
    angular_frequency = 4.79431594e+00
    phase_offset = 2.33387954e+00
    slope_magnitude = 6.11884394e+02
    horizontal_shift = 2.83217492e-02
    period = 9.97641125e-02
    return vertical_offset + amplitude * np.sin(angular_frequency * x + phase_offset) - slope_magnitude * ((x - horizontal_shift) % period)
def pred_bce(x):
    vertical_offset = 1.32146719e+02
    slope_magnitude = 5.92088606e+02
    horizontal_shift = 1.26169775e-01
    period = 1.00159422e-01
    return vertical_offset - slope_magnitude * ((x - horizontal_shift) % period)

def model(input_depature):

    input_depature = pd.to_datetime(input_depature, format="%H:%M") 
    data_errors = pd.read_csv("./errors.csv", index_col=0, parse_dates=["depature"])

    neighbors_acd_errors = np.array(data_errors.loc[
    (data_errors["route"] == "A->C->D")
    & (data_errors["depature"] >= input_depature - pd.Timedelta(minutes=15))
    & (data_errors["depature"] <= input_depature + pd.Timedelta(minutes=15))
    ]["error"])

    neighbors_ace_errors = np.array(data_errors.loc[
    (data_errors["route"] == "A->C->E")
    & (data_errors["depature"] >= input_depature - pd.Timedelta(minutes=15))
    & (data_errors["depature"] <= input_depature + pd.Timedelta(minutes=15))
    ]["error"])

    neighbors_bcd_errors = np.array(data_errors.loc[
    (data_errors["route"] == "B->C->D")
    & (data_errors["depature"] >= input_depature - pd.Timedelta(minutes=15))
    & (data_errors["depature"] <= input_depature + pd.Timedelta(minutes=15))
    ]["error"])

    neighbors_bce_errors = np.array(data_errors.loc[
    (data_errors["route"] == "B->C->E")
    & (data_errors["depature"] >= input_depature - pd.Timedelta(minutes=15))
    & (data_errors["depature"] <= input_depature + pd.Timedelta(minutes=15))
    ]["error"])

    acd_pd10, acd_pd90 = np.percentile(neighbors_acd_errors, [10, 90])
    ace_pd10, ace_pd90 = np.percentile(neighbors_ace_errors, [10, 90])
    bcd_pd10, bcd_pd90 = np.percentile(neighbors_bcd_errors, [10, 90])
    bce_pd10, bce_pd90 = np.percentile(neighbors_bce_errors, [10, 90])

    min_depature = 420
    max_depature  = 1019
    range_depature = max_depature -min_depature
    scaled_input_depature = (input_depature.hour * 60 + input_depature.minute - min_depature) / range_depature

    predicted_acd = pred_acd(scaled_input_depature)
    predicted_ace = pred_ace(scaled_input_depature)
    predicted_bcd = pred_bcd(scaled_input_depature)
    predicted_bce = pred_bce(scaled_input_depature)

    acd_lower = predicted_acd - acd_pd10
    acd_upper = predicted_acd + acd_pd90

    ace_lower = predicted_ace - ace_pd10
    ace_upper = predicted_ace + ace_pd90

    bcd_lower = predicted_bcd - bcd_pd10
    bcd_upper = predicted_bcd + bcd_pd90

    bce_lower = predicted_bce - bce_pd10
    bce_upper = predicted_bce + bce_pd90


    output = Result()

    routs = ["A->C->D", "A->C->E", "B->C->D", "B->C->E"]
    route_scores = np.array([predicted_acd - acd_pd10 + acd_pd90, predicted_ace - ace_pd10 + ace_pd90, predicted_bcd - bcd_pd10 + bcd_pd90, predicted_bce - bce_pd10 + bce_pd90])
    best_route = routs[np.argmin(route_scores)]


    output.best_route = best_route
    output.acd_time = predicted_acd
    output.acd_time_lower = acd_lower
    output.acd_time_upper = acd_upper
    output.ace_time = predicted_ace
    output.ace_time_lower = ace_lower
    output.ace_time_upper = ace_upper
    output.bcd_time = predicted_bcd
    output.bcd_time_lower = bcd_lower
    output.bcd_time_upper = bcd_upper
    output.bce_time = predicted_bce
    output.bce_time_lower = bce_lower
    output.bce_time_upper = bce_upper

    return output


print(model("06:00").best_route)