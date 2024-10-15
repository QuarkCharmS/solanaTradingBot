from websocket_server import WebsocketServer
from buy_and_sell import buy_token_in_raydium, sell_token_in_raydium
from requests import get as httpget
import time, json, subprocess
from datetime import datetime
import sys, os

clients = []

processed_token = {"lp_address": '',
                   "socials": False,
                   "lockedLP_pct": 0.0,
                   "lockedLP_USD": 0.0,
                   "sell_to_buy_ratio": 0.0,
                   "token_rugged": False,
                   "time_waited_in_seconds": 0.0}


def new_client(client, server):
    """

    Websocket function that handles whenever new clients join the session.
    Called for every client with which a handshake is performed.
    """
    print(f"New client connected and was given id {client['id']}")
    clients.append(client)
    server.send_message_to_all(msg='Start.')
    #server.send_message_to_all("Hey all, a new client has joined us")


def client_left(client, server):
    """

    Function called for every client disconnecting from the session.
    """
    print(f"Client({client['id']}) disconnected")


def getJsonFromURI(uri):
    """

    :param uri: uri of the token to retrieve JSON from
    :return: lp JSON information from token
    """

    print(f'uri {uri}')

    response = httpget(uri)
    return json.loads(response.text)


def contains_key(d, keys_to_check):
    """

    :param d: dictionary
    :param keys_to_check: keys in dictionary to check existance of
    :return: True if any of the keys exist, False if none
    """

    for key in d:
        if key in keys_to_check:
            return True
        if isinstance(d[key], dict):
            if contains_key(d[key], keys_to_check):
                return True
    return False

def is_there_social_media(lp_json, keys_to_check):
    processed_token['socials'] = contains_key(lp_json, keys_to_check)


def process_price(price):
    """

    :param price: full price http response from http request
    :return: price in float
    """
    price = price.stdout
    print(f'price : {price}')

    try:
        price = float(price.split('\n')[1].split(' ')[1])
        return price
    except:
        return -1.0

def process_token(token, time_to_wait_in_seconds=60, counter=0, max_retries=3):
    """
    This is the designed function which buys the token and sells it accordingly.
    :param token: address of LP.
    :param time_to_wait_in_seconds: Time to wait in seconds before automatically selling the designated token.
    :param counter: max number of retries before leaving the function.
    :return:
    """

    if counter == 0:
        server.send_message_to_all(msg='Stop.')
        #// Send a message to the client to stop fetching for new LPs through websocket
    initial_price = subprocess.run(f"npx tsx fetchPrices.ts {token}", cwd="./getPrice", shell=True, capture_output=True,
                                   text=True)

    try:
        #// Tries to process the initial price
        initial_price = process_price(initial_price)
    except ValueError:  #// In case that ValueError is received, it means that the price is still not the defined
        #// as the expected answer if the price is not defined should be 'Unable to fetch price.'
        print("Price not available yet... Trying again...")
        time.sleep(5)
        #// Waits 5 seconds before trying to fetch price again.
        if counter == max_retries:
            #// If the maximum number of retries is reached, it stops trying and returns.
            print("Max retries reached.")
            return
        process_token(token, time_to_wait_in_seconds=time_to_wait_in_seconds, counter=counter + 1,
                      max_retries=max_retries)
        return

    print(f'Buy token at price {initial_price}')
    initial_time = time.time()
    #// Starts a timer and every so much so checks if the maximum time has passed

    while True:
        #// Gets current price for token
        price = subprocess.run(f"npx tsx fetchPrices.ts {token}", cwd="./getPrice", shell=True, capture_output=True,
                               text=True)
        try:
            price = process_price(price)
            if price == -1.0:
                raise ValueError
        except ValueError:
            #// In case after the initial token price was fetched and further fetching price fails, it probably means the token was rugged.
            print('error fetching price again')
            print('Token rugged.')
            processed_token['token_rugged'] = True
            return
        print(f'Current price --\n{datetime.now()} - {price}')
        time_passed = time.time() - initial_time

        if (price / initial_price >= 1.5 or time_passed >= time_to_wait_in_seconds):
            #// In case the maximum time passed, then the function is triggered to stop.
            print(f'Selling at price: {price}')
            print(f'Selling is at {100.0 * price / initial_price} of initial price.')

            #// Define the time passed for token and the sell-to-buy ratio
            processed_token['time_waited_in_seconds'] = time_passed
            processed_token['sell_to_buy_ratio'] = price / initial_price
            #// After selling, the program can start fetching for new tokens again.
            break


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
    processed_token['lockedLP_pct'] = lp_locked_pct
    processed_token['lockedLP_USD'] = lp_liquidity_USD


def save_token_data(filename='token-data.txt'):
    content = ''
    print(processed_token.values())
    print(processed_token.keys())
    print(f'processed-token {processed_token}')
    for key in processed_token.keys():
        content = content + f'{processed_token[key]}:'

    with open(filename, 'a+') as file:
        # Move the cursor to the beginning of the file
        file.seek(0)
        # Check if the first character is there (i.e., if the file is empty)
        first_char = file.read(1)
        if first_char:
            # If the file is not empty, move to the end of the file
            file.seek(0, 2)
            # Write the content on a new line
            file.write('\n' + content)
        else:
            # If the file is empty, just write the content
            file.write(content)

def getTokenLockedLP(mint):
    liquidityPoolJSON = subprocess.run(f"node get-pools-by-token.js {mint}", cwd="./getLiquidityFromMint", shell=True, capture_output=True,
                                       text=True).stdout

    start_index = liquidityPoolJSON.find("pubkey:") + len("pubkey:")
    end_index = liquidityPoolJSON[start_index:].find("\n")
    pubkey_value = liquidityPoolJSON[start_index:start_index + end_index].strip().strip("'")

    liquidityInfo = subprocess.run(f"node getLiquidityFromID.js {pubkey_value}", cwd="./getLiquidityFromMint", shell=True, capture_output=True,
                                   text=True).stdout
    print(liquidityInfo)

getTokenLockedLP('BjzqkTKsp3zJtr2P6QR57QkHeEhNzTXDEh3zSv4Npump')


# Called when a client sends a message
def new_token_received(token):
    print('########################################################NEW TOKEN FETCHED')

    global processed_token
    processed_token = {"lp_address": token,
    "socials": False,
    "lockedLP_pct": 0.0,
    "lockedLP_USD": 0.0,
    "sell_to_buy_ratio": 0.0,
    "token_rugged": False,
    "time_waited_in_seconds": 0.0}

    """
    Whenever a new LP_Token is received through websocket, it is processed directly by this function.

    """
    if len(token) > 200:
        message = token[:200] + '..'
    print(
        f"New token fetched: {token}")  #// Whenever a notification of a new token is recieved, it has to get processed

    socials = subprocess.run(f"node getMetadata.mjs {token}", cwd="./get-Metadata", shell=True, capture_output=True,
                             text=True)
    #// Process what are the socials for token
    uri = socials.stdout
    uri = ''.join(uri.split())

    processed_token['lp_address'] = token
    try:
        lp_data = getJsonFromURI(uri)
        lp_name = lp_data.get('name')
        print(f'name : {lp_name}')
        keys_to_check = {'telegram', 'twitter', 'facebook', 'site', 'socials', 'social'}

        print('Checking for social media')
        is_there_social_media(lp_data, keys_to_check)

        print('Checking for locked liquidity of token')
        check_locked_liquidity(token)

        if lp_name == "$Peloki":
            print('Test Token, ignore')
            return
    except Exception as e:
        print(e)
        print('Something went wrong parsing into json')
        return

    process_token(token, time_to_wait_in_seconds=15)

    save_token_data()
    server.send_message_to_all(msg='Start.')

def new_message(client, server, token):
    new_token_received(token)

PORT = 6789
HOST = ""
server = WebsocketServer(HOST, PORT)
#server.set_fn_new_client(new_client)
#server.set_fn_client_left(client_left)
#server.set_fn_message_received(new_message)
#server.run_forever()
