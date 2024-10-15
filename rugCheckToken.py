from requests import get
import json
import time


while True:
    response = get('https://api.rugcheck.xyz/v1/tokens/DZGUSx93beXdJCGVXYdgveUX5cH5S5W9MJW26RjCS26n/report')

    print(response.json())
    print(json.dumps(response.json(), indent=2))
    #print(json.dumps(response.json()["markets"][0]["lp"]["lpLockedPct"], indent=2))
    time.sleep(1)

    data=response.json()

    if 'markets' in data and data['markets'] is not None:
        market = data['markets'][0]
        if 'lp' in market and 'lpLockedPct' in market['lp']:
            lp_locked_pct = market['lp']['lpLockedPct']
            print(f"The lpLockedPct is: {lp_locked_pct}")
        else:
            print("The field 'lpLockedPct' does not exist.")
    else:
        print("The field 'markets' does not exist or is empty.")


    break