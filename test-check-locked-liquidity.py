import time
from requests import get as httpget

def check_locked_liquidity(token, counter=0, max_retries=3):
    """
    Function tries to use rugcheck to verify if there exists locked liquidity for token.
    :param token: token address
    :param counter: number of times this function was tried yet
    :param max_retries: maximum number of retries until exiting unsuccessful
    :return: locked liquidity in USD, locked liquidity percentage
    """

    if counter == max_retries:
        print('Max retries reached for the program.')
        return 'invalid', 'invalid'

    lp_liquidity_USD, lp_locked_pct = 'invalid', 'invalid'

    response = httpget(f'https://api.rugcheck.xyz/v1/tokens/{token}/report')
    data = response.json()
    #// Queries rugcheck to check for the existance of any possible locked liquidity

    if 'markets' in data and data['markets'] is not None:
        market = data['markets'][0]
        #// Check if the market is already open
        if 'lp' in market and 'lpLockedPct' in market['lp'] and 'lpLockedUSD' in market['lp']:
            lp_locked_pct = market['lp']['lpLockedPct']
            lp_liquidity_USD = market['lp']['lpLockedUSD']
        elif 'lp' in market and 'lpLockedPct' in market['lp']:
            lp_locked_pct = market['lp']['lpLockedPct']
        elif 'lp' in market and 'lpLockedUSD' in market['lp']:
            lp_liquidity_USD = market['lp']['lpLockedUSD']
        else:
            print("Could not find the field 'lpLockedPct', trying again...")
            time.sleep(10)
            check_locked_liquidity(token, counter + 1)
            return
    else:
        print("Could not find the field 'markets', trying again...")
        time.sleep(10)
        check_locked_liquidity(token, counter + 1)
        return

    #// Define the liquidity information of token
    print(lp_locked_pct)
    print(lp_liquidity_USD)

check_locked_liquidity('5bv5XoLb4RgZgc4joghGPfyN5fwdVqfkYQyYQfFPpump')