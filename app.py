from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime, timedelta, timezone
import os
import json 
from math import exp



app = Flask(__name__)
app.secret_key = "menloSourcing"
app.permanent_session_lifetime = timedelta(minutes=10)  # Session timeout duration




with open("jsonVals.json", 'r') as json_file:
    base_rates = json.load(json_file)


with open("smoothed_probabilities.json", 'r') as json_file:
    arr = json.load(json_file)

float_keys = [float(key) for key in arr.keys()]



with open("PitchBook.json", 'r') as json_file:
    pb = json.load(json_file)


valuations = [    "Post valuation: 0-10m",    "Post valuation: 10m-25m",    "Post valuation: 25m-50m",    "Post valuation: 50m-75m",    "Post valuation: 75m-150m",    "Post valuation: 150m-300m",    "Post valuation: 300m-500m",    "Post valuation: 500m-750m",    "Post valuation: 750m-1b",    "Post valuation: 1b-2b",    "Post valuation: 2b-5b",    "Post valuation: 5b+"]


def find_valuation_index(i):
    if i < 0:
        return None  # If i is negative, it's not in any range

    # Define the corresponding numeric ranges for comparison
    ranges = [
        (0, 10_000_000), (10_000_000, 25_000_000), (25_000_000, 50_000_000),
        (50_000_000, 75_000_000), (75_000_000, 150_000_000),
        (150_000_000, 300_000_000), (300_000_000, 500_000_000),
        (500_000_000, 750_000_000), (750_000_000, 1_000_000_000),
        (1_000_000_000, 2_000_000_000), (2_000_000_000, 5_000_000_000),
        (5_000_000_000, float('inf'))
    ]

    for index, (low, high) in enumerate(ranges):
        if low <= i < high:
            return index
    
    return None  # If i doesn't fit in any range, return None



def sigFigProbs(probability):
    if probability is not None:
        formatted_percentage = "{:.3g}%".format(100 * probability)
        if formatted_percentage == '0.00%':
            formatted_percentage = "{:.3e}%".format(100 * probability)
    else:
        formatted_percentage = "N/A"

    return formatted_percentage

# Hardcoded credentials
PASSWORD = "menloSourcing"




@app.route('/', methods=['GET', 'POST'])
def index():
    if 'authenticated' in session and session['authenticated']:
        last_activity = session.get('last_activity', None)
        if last_activity:
            # Check if last_activity is already timezone-aware
            if last_activity.tzinfo is None:
                # If not, localize it
                last_activity = last_activity.replace(tzinfo=timezone.utc)

            now = datetime.now(timezone.utc)  # Get current UTC time

            if now - last_activity > app.permanent_session_lifetime:
                # Session has expired, force the user to log in again
                session.clear()
                return redirect(url_for('login'))
        else:
            # Update the last activity time
            session['last_activity'] = datetime.now(timezone.utc)

        
        if request.method == 'POST':
            roundVal = request.form['round']
            lastroundvaluation = request.form['lastroundvaluation'] 
            equity = request.form['equity'] 
            sector = request.form['sector']
            
            arrInput = request.form['arrinput']
            if arrInput == '':
                arrInput = 0
            
            try:
                arrInput = int(arrInput)
            except:
                arrInput = 0
            

            if lastroundvaluation == '':
                lastroundvaluation = 0
            if equity == '':
                equity = 0
            try:
                lastroundvaluation = int(lastroundvaluation)
            except:
                lastroundvaluation = 0
            try:
                equity = int(equity)
            except:
                equity = 0

            

            if(lastroundvaluation == 0 or roundVal == "Private Equity" or roundVal == "Pre Seed"):

                base_rate_next_round = "{:.2f}%".format(100 * base_rates[sector][roundVal].get('Next round %', 0)) if base_rates[sector][roundVal].get('Next round %', 0) != "N/A" else "N/A"
                base_rate_exit = "{:.2f}%".format(100 * base_rates[sector][roundVal].get('Exit round %', 0)) if base_rates[sector][roundVal].get('Exit round %', 0) != "N/A" else "N/A"
                exit_lt_200M = "{:.2f}%".format(100 * base_rates[sector][roundVal].get('Exit < 200M %', 0)) if base_rates[sector][roundVal].get('Exit < 200M %', 0) != "N/A" else "N/A"
                exit_200M_500M = "{:.2f}%".format(100 * base_rates[sector][roundVal].get('Exit 200M-500M %', 0)) if base_rates[sector][roundVal].get('Exit 200M-500M %', 0) != "N/A" else "N/A"
                exit_500M_1B = "{:.2f}%".format(100 * base_rates[sector][roundVal].get('Exit 500M-1B %', 0)) if base_rates[sector][roundVal].get('Exit 500M-1B %', 0) != "N/A" else "N/A"
                exit_1B_2B = "{:.2f}%".format(100 * base_rates[sector][roundVal].get('Exit 1B-2B %', 0)) if base_rates[sector][roundVal].get('Exit 1B-2B %', 0) != "N/A" else "N/A"
                exit_2B_5B = "{:.2f}%".format(100 * base_rates[sector][roundVal].get('Exit 2B-5B %', 0)) if base_rates[sector][roundVal].get('Exit 2B-5B %', 0) != "N/A" else "N/A"
                exit_5B_10B = "{:.2f}%".format(100 * base_rates[sector][roundVal].get('Exit 5B-10B %', 0)) if base_rates[sector][roundVal].get('Exit 5B-10B %', 0) != "N/A" else "N/A"
                exit_gt_10B = "{:.2f}%".format(100 * base_rates[sector][roundVal].get('Exit > 10 B %', 0)) if base_rates[sector][roundVal].get('Exit > 10 B %', 0) != "N/A" else "N/A"
                exit_no_valuation = "{:.2f}%".format(100 * base_rates[sector][roundVal].get('Exit no Valuation %', 0)) if base_rates[sector][roundVal].get('Exit no Valuation %', 0) != "N/A" else "N/A"
                median_headcount = str(round(int(base_rates[sector][roundVal].get('Median headcount', 0)))) if base_rates[sector][roundVal].get('Median headcount', 0) != "N/A" else "N/A"
                estimated_arr_per_fte = "${:,.0f}".format(round(int(base_rates[sector][roundVal].get('Estimated ARR per FTE from Headcount + ICONIQ report', 0)))) if base_rates[sector][roundVal].get('Estimated ARR per FTE from Headcount + ICONIQ report', 0) != "N/A" else "N/A"
                estimated_arr = "${:,.0f}".format(round(int(base_rates[sector][roundVal].get('Estimated ARR', 0)))) if base_rates[sector][roundVal].get('Estimated ARR', 0) != "N/A" else "N/A"
                average_funding = "${:,.0f}".format(round(int(base_rates[sector][roundVal].get('Average funding', 0)))) if base_rates[sector][roundVal].get('Average funding', 0) != "N/A" else "N/A"
                median_funding = "${:,.0f}".format(round(int(base_rates[sector][roundVal].get('Median funding', 0)))) if base_rates[sector][roundVal].get('Median funding', 0) != "N/A" else "N/A"
                avg_time_to_next_round_typical = str(round(int(base_rates[sector][roundVal].get('Average time to next round in typical series (days)', 0)))) + " days" if base_rates[sector][roundVal].get('Average time to next round in typical series (days)', 0) != "N/A" else "N/A"
                median_time_to_next_round_typical = str(round(int(base_rates[sector][roundVal].get('Median time to next round in typical series(days)', 0)))) + " days" if base_rates[sector][roundVal].get('Median time to next round in typical series(days)', 0) != "N/A" else "N/A"
                avg_time_to_any_next_round = str(round(int(base_rates[sector][roundVal].get('Average time to any next round (days)', 0)))) + " days" if base_rates[sector][roundVal].get('Average time to any next round (days)', 0) != "N/A" else "N/A"
                median_time_to_any_next_round = str(round(int(base_rates[sector][roundVal].get('Median time to any next round (days)', 0)))) + " days" if base_rates[sector][roundVal].get('Median time to any next round (days)', 0) != "N/A" else "N/A"
                avg_time_to_exit = str(round(int(base_rates[sector][roundVal].get('average time to exit (days)', 0)))) + " days" if base_rates[sector][roundVal].get('average time to exit (days)', 0) != "N/A" else "N/A"
                median_time_to_exit = str(round(int(base_rates[sector][roundVal].get('Median time to exit (days)', 0)))) + " days" if base_rates[sector][roundVal].get('Median time to exit (days)', 0) != "N/A" else "N/A"
                expected_value_of_outcome = round(int(base_rates[sector][roundVal].get('Expected value of outcome', 0))) if base_rates[sector][roundVal].get('Expected value of outcome', 0) != "N/A" else "N/A"

                
                closest_key = None
                for key in sorted(float_keys):
                    closest_key = key
                    if key >= arrInput/1000000:
                        break
                if(closest_key is None):
                    closest_key = sorted(float_keys)[-1]

                probs = arr[str(closest_key)]
                pARR1 = sigFigProbs(probs.get('prob_0_2', 0))
                pARR2 = sigFigProbs(probs.get('prob_2_5', 0))
                pARR3 = sigFigProbs(probs.get('prob_5_10', 0))
                pARR4 = sigFigProbs(probs.get('prob_10_20', 0))
                pARR5 = sigFigProbs(probs.get('prob_20_50', 0))
                pARR6 = sigFigProbs(probs.get('prob_50_100', 0))
                pARR7 = sigFigProbs(probs.get('prob_100_500', 0))
                pARR8 = sigFigProbs(probs.get('prob_500_1000', 0))
                pARR9 = sigFigProbs(probs.get("prob_1000_inf", 0))
                

                '''
                #these lines for temp only
                pARR1 = None
                pARR2 = None
                pARR3 = None
                pARR4 = None
                pARR5 = None
                pARR6 = None
                pARR7 = None
                pARR8 = None
                pARR9 = None
                arrInput = 0
                '''

                meanExit = int(equity)*expected_value_of_outcome/100
                try:
                    prob_gain_0_500K = "{:.2f}%".format(100 *(1-exp(-(1/meanExit)*500000)) * base_rates[sector][roundVal].get('Exit round %', 0))
                    prob_gain_500K_1M = "{:.2f}%".format(100 *((1-exp(-(1/meanExit)*1000000)) - (1-exp(-(1/meanExit)*500000))) * base_rates[sector][roundVal].get('Exit round %', 0))
                    prob_gain_1_5M = "{:.2f}%".format(100 *((1-exp(-(1/meanExit)*5000000)) - (1-exp(-(1/meanExit)*1000000))) * base_rates[sector][roundVal].get('Exit round %', 0))
                    prob_gain_5M_10M = "{:.2f}%".format(100 *((1-exp(-(1/meanExit)*10000000)) - (1-exp(-(1/meanExit)*5000000))) * base_rates[sector][roundVal].get('Exit round %', 0))
                    prob_gain_10M_plus = "{:.2f}%".format(100 *(1 - (1-exp(-(1/meanExit)*10000000))) * base_rates[sector][roundVal].get('Exit round %', 0))
                except:
                    prob_gain_0_500K = 0
                    prob_gain_500K_1M = 0
                    prob_gain_1_5M = 0
                    prob_gain_5M_10M = 0
                    prob_gain_10M_plus = 0    
                



                # Inside the index() function
                return render_template('result.html', round=roundVal, lastroundvaluation=lastroundvaluation, inputARR = arrInput, equity="{:.2f}%".format(int(equity)), sector=sector, base_rate_next_round=base_rate_next_round, base_rate_exit=base_rate_exit, exit_lt_200M=exit_lt_200M, exit_200M_500M=exit_200M_500M, exit_500M_1B=exit_500M_1B, exit_1B_2B=exit_1B_2B, exit_2B_5B=exit_2B_5B, exit_5B_10B=exit_5B_10B, exit_gt_10B=exit_gt_10B, exit_no_valuation=exit_no_valuation, median_headcount=median_headcount, estimated_arr_per_fte=estimated_arr_per_fte, estimated_arr=estimated_arr, average_funding=average_funding, median_funding=median_funding, avg_time_to_next_round_typical=avg_time_to_next_round_typical, median_time_to_next_round_typical=median_time_to_next_round_typical, avg_time_to_any_next_round=avg_time_to_any_next_round, median_time_to_any_next_round=median_time_to_any_next_round, avg_time_to_exit=avg_time_to_exit, median_time_to_exit=median_time_to_exit, expected_value_of_outcome= "${:,.0f}".format(round(expected_value_of_outcome*int(equity)/100))
                                    , prob_gain_0_500K=prob_gain_0_500K, prob_gain_500K_1M=prob_gain_500K_1M, prob_gain_1_5M=prob_gain_1_5M, prob_gain_5M_10M=prob_gain_5M_10M, prob_gain_10M_plus=prob_gain_10M_plus,
                                    pARR1=pARR1, pARR2=pARR2, pARR3=pARR3, pARR4=pARR4, pARR5=pARR5, pARR6=pARR6, pARR7=pARR7, pARR8=pARR8, pARR9=pARR9 )


            else:

                valIndex = find_valuation_index(lastroundvaluation)

                next1 = "{:.2f}%".format(100 * pb[roundVal][valuations[valIndex]]["Next Round:"].get("0-10m", 0)) if pb[roundVal][valuations[valIndex]]["Next Round:"].get("0-10m", None) is not None else "N/A"
                next2 = "{:.2f}%".format(100 * pb[roundVal][valuations[valIndex]]["Next Round:"].get("10m-25m", 0)) if pb[roundVal][valuations[valIndex]]["Next Round:"].get("10m-25m", None) is not None else "N/A"
                next3 = "{:.2f}%".format(100 * pb[roundVal][valuations[valIndex]]["Next Round:"].get("25m-50m", 0)) if pb[roundVal][valuations[valIndex]]["Next Round:"].get("25m-50m", None) is not None else "N/A"
                next4 = "{:.2f}%".format(100 * pb[roundVal][valuations[valIndex]]["Next Round:"].get("50m-75m", 0)) if pb[roundVal][valuations[valIndex]]["Next Round:"].get("50m-75m", None) is not None else "N/A"
                next5 = "{:.2f}%".format(100 * pb[roundVal][valuations[valIndex]]["Next Round:"].get("75m-150m", 0)) if pb[roundVal][valuations[valIndex]]["Next Round:"].get("75m-150m", None) is not None else "N/A"
                next6 = "{:.2f}%".format(100 * pb[roundVal][valuations[valIndex]]["Next Round:"].get("150m-300m", 0)) if pb[roundVal][valuations[valIndex]]["Next Round:"].get("150m-300m", None) is not None else "N/A"
                next7 = "{:.2f}%".format(100 * pb[roundVal][valuations[valIndex]]["Next Round:"].get("300m-500m", 0)) if pb[roundVal][valuations[valIndex]]["Next Round:"].get("300m-500m", None) is not None else "N/A"
                next8 = "{:.2f}%".format(100 * pb[roundVal][valuations[valIndex]]["Next Round:"].get("500m-750m", 0)) if pb[roundVal][valuations[valIndex]]["Next Round:"].get("500m-750m", None) is not None else "N/A"
                next9 = "{:.2f}%".format(100 * pb[roundVal][valuations[valIndex]]["Next Round:"].get("750m-1b", 0)) if pb[roundVal][valuations[valIndex]]["Next Round:"].get("750m-1b", None) is not None else "N/A"
                next10 = "{:.2f}%".format(100 * pb[roundVal][valuations[valIndex]]["Next Round:"].get("1b-2b", 0)) if pb[roundVal][valuations[valIndex]]["Next Round:"].get("1b-2b", None) is not None else "N/A"
                next11 = "{:.2f}%".format(100 * pb[roundVal][valuations[valIndex]]["Next Round:"].get("2b-5b", 0)) if pb[roundVal][valuations[valIndex]]["Next Round:"].get("2b-5b", None) is not None else "N/A"
                next12 = "{:.2f}%".format(100 * pb[roundVal][valuations[valIndex]]["Next Round:"].get("5b+", 0)) if pb[roundVal][valuations[valIndex]]["Next Round:"].get("5b+", None) is not None else "N/A"

                exit1 = "{:.2f}%".format(100 * pb[roundVal][valuations[valIndex]]["Exit"].get("0-200m", 0)) if pb[roundVal][valuations[valIndex]]["Exit"].get("0-200m", None) is not None else "N/A"
                exit2 = "{:.2f}%".format(100 * pb[roundVal][valuations[valIndex]]["Exit"].get("200m-500m", 0)) if pb[roundVal][valuations[valIndex]]["Exit"].get("200m-500m", None) is not None else "N/A"
                exit3 = "{:.2f}%".format(100 * pb[roundVal][valuations[valIndex]]["Exit"].get("500m-1b", 0)) if pb[roundVal][valuations[valIndex]]["Exit"].get("500m-1b", None) is not None else "N/A"
                exit4 = "{:.2f}%".format(100 * pb[roundVal][valuations[valIndex]]["Exit"].get("1b-2b", 0)) if pb[roundVal][valuations[valIndex]]["Exit"].get("1b-2b", None) is not None else "N/A"
                exit5 = "{:.2f}%".format(100 * pb[roundVal][valuations[valIndex]]["Exit"].get("2b-5b", 0)) if pb[roundVal][valuations[valIndex]]["Exit"].get("2b-5b", None) is not None else "N/A"
                exit6 = "{:.2f}%".format(100 * pb[roundVal][valuations[valIndex]]["Exit"].get("5b+", 0)) if pb[roundVal][valuations[valIndex]]["Exit"].get("5b+", None) is not None else "N/A"

                median_headcount = str(round(int(base_rates[sector][roundVal].get('Median headcount', 0)))) if base_rates[sector][roundVal].get('Median headcount', 0) != "N/A" else "N/A"
                estimated_arr_per_fte = "${:,.0f}".format(round(int(base_rates[sector][roundVal].get('Estimated ARR per FTE from Headcount + ICONIQ report', 0)))) if base_rates[sector][roundVal].get('Estimated ARR per FTE from Headcount + ICONIQ report', 0) != "N/A" else "N/A"
                estimated_arr = "${:,.0f}".format(round(int(base_rates[sector][roundVal].get('Estimated ARR', 0)))) if base_rates[sector][roundVal].get('Estimated ARR', 0) != "N/A" else "N/A"
                average_funding = "${:,.0f}".format(round(int(base_rates[sector][roundVal].get('Average funding', 0)))) if base_rates[sector][roundVal].get('Average funding', 0) != "N/A" else "N/A"
                median_funding = "${:,.0f}".format(round(int(base_rates[sector][roundVal].get('Median funding', 0)))) if base_rates[sector][roundVal].get('Median funding', 0) != "N/A" else "N/A"
                avg_time_to_next_round_typical = str(round(int(base_rates[sector][roundVal].get('Average time to next round in typical series (days)', 0)))) + " days" if base_rates[sector][roundVal].get('Average time to next round in typical series (days)', 0) != "N/A" else "N/A"
                median_time_to_next_round_typical = str(round(int(base_rates[sector][roundVal].get('Median time to next round in typical series(days)', 0)))) + " days" if base_rates[sector][roundVal].get('Median time to next round in typical series(days)', 0) != "N/A" else "N/A"
                avg_time_to_any_next_round = str(round(int(base_rates[sector][roundVal].get('Average time to any next round (days)', 0)))) + " days" if base_rates[sector][roundVal].get('Average time to any next round (days)', 0) != "N/A" else "N/A"
                median_time_to_any_next_round = str(round(int(base_rates[sector][roundVal].get('Median time to any next round (days)', 0)))) + " days" if base_rates[sector][roundVal].get('Median time to any next round (days)', 0) != "N/A" else "N/A"
                avg_time_to_exit = str(round(int(base_rates[sector][roundVal].get('average time to exit (days)', 0)))) + " days" if base_rates[sector][roundVal].get('average time to exit (days)', 0) != "N/A" else "N/A"
                median_time_to_exit = str(round(int(base_rates[sector][roundVal].get('Median time to exit (days)', 0)))) + " days" if base_rates[sector][roundVal].get('Median time to exit (days)', 0) != "N/A" else "N/A"
                expected_value_of_outcome = round(int(base_rates[sector][roundVal].get('Expected value of outcome', 0))) if base_rates[sector][roundVal].get('Expected value of outcome', 0) != "N/A" else "N/A"
                
                
                closest_key = None
                for key in sorted(float_keys):
                    closest_key = key
                    if key >= arrInput/1000000:
                        break
                if(closest_key is None):
                    closest_key = sorted(float_keys)[-1]

                probs = arr[str(closest_key)]
                pARR1 = sigFigProbs(probs.get('prob_0_2', 0))
                pARR2 = sigFigProbs(probs.get('prob_2_5', 0))
                pARR3 = sigFigProbs(probs.get('prob_5_10', 0))
                pARR4 = sigFigProbs(probs.get('prob_10_20', 0))
                pARR5 = sigFigProbs(probs.get('prob_20_50', 0))
                pARR6 = sigFigProbs(probs.get('prob_50_100', 0))
                pARR7 = sigFigProbs(probs.get('prob_100_500', 0))
                pARR8 = sigFigProbs(probs.get('prob_500_1000', 0))
                pARR9 = sigFigProbs(probs.get("prob_1000_inf", 0))
                

                '''
                #these lines for temp only
                pARR1 = None
                pARR2 = None
                pARR3 = None
                pARR4 = None
                pARR5 = None
                pARR6 = None
                pARR7 = None
                pARR8 = None
                pARR9 = None
                arrInput = 0
                '''

                meanExit = int(equity)*expected_value_of_outcome/100
                try:
                    prob_gain_0_500K = "{:.2f}%".format(100 *(1-exp(-(1/meanExit)*500000)) * base_rates[sector][roundVal].get('Exit round %', 0))
                    prob_gain_500K_1M = "{:.2f}%".format(100 *((1-exp(-(1/meanExit)*1000000)) - (1-exp(-(1/meanExit)*500000))) * base_rates[sector][roundVal].get('Exit round %', 0))
                    prob_gain_1_5M = "{:.2f}%".format(100 *((1-exp(-(1/meanExit)*5000000)) - (1-exp(-(1/meanExit)*1000000))) * base_rates[sector][roundVal].get('Exit round %', 0))
                    prob_gain_5M_10M = "{:.2f}%".format(100 *((1-exp(-(1/meanExit)*10000000)) - (1-exp(-(1/meanExit)*5000000))) * base_rates[sector][roundVal].get('Exit round %', 0))
                    prob_gain_10M_plus = "{:.2f}%".format(100 *(1 - (1-exp(-(1/meanExit)*10000000))) * base_rates[sector][roundVal].get('Exit round %', 0))
                except:
                    prob_gain_0_500K = 0
                    prob_gain_500K_1M = 0
                    prob_gain_1_5M = 0
                    prob_gain_5M_10M = 0
                    prob_gain_10M_plus = 0    
                


                # Inside the index() function
                return render_template('resultPB.html', round=roundVal, lastroundvaluation=lastroundvaluation, inputARR = arrInput, equity="{:.2f}%".format(int(equity)), sector=sector, median_headcount=median_headcount, estimated_arr_per_fte=estimated_arr_per_fte, estimated_arr=estimated_arr, average_funding=average_funding, median_funding=median_funding, avg_time_to_next_round_typical=avg_time_to_next_round_typical, median_time_to_next_round_typical=median_time_to_next_round_typical, avg_time_to_any_next_round=avg_time_to_any_next_round, median_time_to_any_next_round=median_time_to_any_next_round, avg_time_to_exit=avg_time_to_exit, median_time_to_exit=median_time_to_exit, expected_value_of_outcome= "${:,.0f}".format(round(expected_value_of_outcome*int(equity)/100))
                                    , prob_gain_0_500K=prob_gain_0_500K, prob_gain_500K_1M=prob_gain_500K_1M, prob_gain_1_5M=prob_gain_1_5M, prob_gain_5M_10M=prob_gain_5M_10M, prob_gain_10M_plus=prob_gain_10M_plus,
                                    pARR1=pARR1, pARR2=pARR2, pARR3=pARR3, pARR4=pARR4, pARR5=pARR5, pARR6=pARR6, pARR7=pARR7, pARR8=pARR8,
                                    next1=next1, next2=next2, next3=next3, next4=next4, next5=next5, next6=next6, next7=next7, next8=next8, next9=next9, next10=next10, next11=next11, next12=next12,
                                    exit1=exit1, exit2=exit2, exit3=exit3, exit4=exit4, exit5=exit5, exit6=exit6 )




        return render_template('index.html')
    else:
        # User is not authenticated, redirect to the login page
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if password == PASSWORD:
            # Authentication successful
            session['authenticated'] = True
            return redirect(url_for('index'))
        else:
            # Authentication failed
            error = "Invalid username or password"
            return render_template('login.html', error=error)
    return render_template('login.html')


if __name__ == '__main__':
    app.run(host="127.0.0.1",port=8000, debug=True)