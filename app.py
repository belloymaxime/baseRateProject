from flask import Flask, render_template, request
import json 
from math import exp



app = Flask(__name__)

# Dummy database of base rates



with open("jsonVals.json", 'r') as json_file:
    base_rates = json.load(json_file)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        roundVal = request.form['round']
        lastroundvaluation = request.form['lastroundvaluation'] 
        equity = request.form['equity'] 
        sector = request.form['sector']
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
        median_headcount = str(round(int(base_rates[sector][roundVal].get('Median headcount', 0)))) + " days" if base_rates[sector][roundVal].get('Median headcount', 0) != "N/A" else "N/A"
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
        return render_template('result.html', round=roundVal, lastroundvaluation=lastroundvaluation, equity="{:.2f}%".format(int(equity)), sector=sector, base_rate_next_round=base_rate_next_round, base_rate_exit=base_rate_exit, exit_lt_200M=exit_lt_200M, exit_200M_500M=exit_200M_500M, exit_500M_1B=exit_500M_1B, exit_1B_2B=exit_1B_2B, exit_2B_5B=exit_2B_5B, exit_5B_10B=exit_5B_10B, exit_gt_10B=exit_gt_10B, exit_no_valuation=exit_no_valuation, median_headcount=median_headcount, estimated_arr_per_fte=estimated_arr_per_fte, estimated_arr=estimated_arr, average_funding=average_funding, median_funding=median_funding, avg_time_to_next_round_typical=avg_time_to_next_round_typical, median_time_to_next_round_typical=median_time_to_next_round_typical, avg_time_to_any_next_round=avg_time_to_any_next_round, median_time_to_any_next_round=median_time_to_any_next_round, avg_time_to_exit=avg_time_to_exit, median_time_to_exit=median_time_to_exit, expected_value_of_outcome= "${:,.0f}".format(round(expected_value_of_outcome*int(equity)/100))
                               , prob_gain_0_500K=prob_gain_0_500K, prob_gain_500K_1M=prob_gain_500K_1M, prob_gain_1_5M=prob_gain_1_5M, prob_gain_5M_10M=prob_gain_5M_10M, prob_gain_10M_plus=prob_gain_10M_plus)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=8080, debug=True)