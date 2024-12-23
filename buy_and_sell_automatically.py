###IMPORTS

from time import sleep
from websocket_server import WebsocketServer
import time, json, subprocess
from datetime import datetime
import asyncio
from colorama import Style, Fore
import httpx
from buy_and_sell_jupiter_async import buy_with_sol, sell_to_sol

### WEBSOCKET METHODS

clients = []

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

def new_message(client, server, token):
    asyncio.run(new_token_received(token))


def exit_gracefully(something, something2):
    server.send_message_to_all(msg='Stop Completely.')
    exit(0)


### UTILITY METHODS

async def async_httpget(url):
    """
    Since the code we want to run is asynchronous in nature, we will need to make sure all the processes which run in the code
    support asynchronous processing. Since the classic requests library is a synchronous library, using httpx is the correct choice
    in this case since httpx supports asynchronous processing.

    :param url: URL to make a get request to
    :return: Response given by server
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response

async def getJsonFromURI(uri):
    """

    :param uri: uri of the token to retrieve JSON from
    :return: lp JSON information from token
    """

    print(f'uri {uri}')

    response = await async_httpget(uri)
    print(response)
    return json.loads(response.text)

def process_price(price):
    """

    :param price: full price http response from http request
    :return: price in float
    """
    #price = price.stdout
    print(f'price : {price}')

    try:
        price = float(price.split('\n')[1].split(' ')[1])
        return price
    except:
        return -1.0

def save_token_data(filename='token-data.txt'):
    lp_information = f"{processed_token.get('lp_address')}"
    print(processed_token.values())
    print(processed_token.keys())
    print(f'processed-token {processed_token}')
    for key in processed_token.keys():
        if key == 'lp_address':
            continue
        lp_information = lp_information + f':{processed_token[key]}'

    with open(filename, 'a+') as file:
        # Move the cursor to the beginning of the file
        file.seek(0)
        # Check if the first character is there (i.e., if the file is empty)
        first_char = file.read(1)
        if first_char:
            # If the file is not empty, move to the end of the file
            file.seek(0, 2)
            # Write the content on a new line
            file.write('\n'+lp_information)
        else:
            # If the file is empty, just write the content
            file.write(lp_information)


### WORKFLOW FUNCTIONS

processed_token = {"lp_address": '',
                   "sell_to_buy_ratio": 0.0,
                   "token_rugged": False,
                   "time_waited_in_seconds": 0.0}

async def process_token(token, time_to_wait_in_seconds=60, counter=0, max_retries=3):
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
    #initial_price = subprocess.run(f"npx tsx fetchPrices.ts {token}", cwd="./getPrice", shell=True, capture_output=True, text=True)
    proc = await asyncio.create_subprocess_shell(
                                            f"npx tsx fetchPrices.ts {token}",
                                                 cwd="./getPrice",
                                                 stdout=asyncio.subprocess.PIPE,
                                                 stderr=asyncio.subprocess.PIPE
                                                )
    stdout, stderr = await proc.communicate()

    initial_price = stdout.decode('utf-8')
    stderr = stderr.decode('utf-8')

    try:
        if proc.returncode != 0:
            raise RuntimeError
        #// Tries to process the initial price
        initial_price = process_price(initial_price)
        sleep(3)
        if initial_price == -1.0:
            raise ValueError
    except ValueError:  #// In case that ValueError is received, it means that the price is still not the defined
        #// as the expected answer if the price is not defined should be 'Unable to fetch price.'
        print("Price not available yet... Trying again...")
        time.sleep(3)
        #// Waits 5 seconds before trying to fetch price again.
        if counter == max_retries:
            #// If the maximum number of retries is reached, it stops trying and returns.
            print("Max retries reached.")
            return
        await process_token(token, time_to_wait_in_seconds=time_to_wait_in_seconds, counter=counter + 1,
                      max_retries=max_retries)
        return
    except RuntimeError:
        print('Failed to run process to fetch price (intial_price)')
        print("ERROR:\n" + Fore.RED + stderr + Style.RESET_ALL)
        print("Something happened while trying to fetch information about the token... Aborting...")
        return

    print(f'Buy token at price {initial_price}')
    try:
        await buy_with_sol(token)
    except Exception as e:
        print(f'Unexpected error happened: {e}')
        return

    initial_time = time.time()

    #// Starts a timer and every so much so checks if the maximum time has passed

    while True:
        #// Gets current price for token
        #price = subprocess.run(f"npx tsx fetchPrices.ts {token}", cwd="./getPrice", shell=True, capture_output=True, text=True)
        proc = await asyncio.create_subprocess_shell(
            f"npx tsx fetchPrices.ts {token}",
            cwd="./getPrice",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()

        price = stdout.decode('utf-8')
        stderr = stderr.decode('utf-8')

        if proc.returncode != 0:
            print('Failed to run process for fetching price')
            print("ERROR:\n" + Fore.RED + stderr + Style.RESET_ALL)
            raise RuntimeError

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
        except RuntimeError:
            print("Something happened while trying to fetch information about the token... Aborting...")
            return
        print(f'Current price --\n{datetime.now()} - {price}')
        time_passed = time.time() - initial_time
        print(f'Comparison to initial price: {100*(price/initial_price)}%')

        if (price / initial_price >= 1.2 or time_passed >= time_to_wait_in_seconds):
            #// In case the maximum time passed, then the function is triggered to stop.
            print(f'Selling at price: {price}')
            print(f'Selling is at {100.0 * price / initial_price}% of initial price.')

            try:
                await sell_to_sol(token)
            except Exception as e:
                print(f'Some unexpected error ocurred when trying to sell token {e}')
                print(f'token: {token}')
                return

            #// Define the time passed for token and the sell-to-buy ratio
            processed_token['time_waited_in_seconds'] = time_passed
            processed_token['sell_to_buy_ratio'] = price / initial_price
            #// After selling, the program can start fetching for new tokens again.
            break

async def new_token_received(token):
    """
        Whenever a new LP_Token is received through websocket, it is processed directly by this function.

    :param token: lpMint token of the liquidity pool needed to process
    """

    print('########################################################NEW TOKEN FETCHED')

    global processed_token
    processed_token = {"lp_address": token,
    "sell_to_buy_ratio": 0.0,
    "token_rugged": False,
    "time_waited_in_seconds": 0.0}

    if len(token) > 200:
        message = token[:200] + '..'
    print(
        f"New token fetched: {token}")  #// Whenever a notification of a new token is recieved, it has to get processed

    processed_token['lp_address'] = token

    print('Checking for locked liquidity of token')

    if token == 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v':
        print('Token fetched is test token')
        return

    print('Starting to process token...')
    await process_token(token, time_to_wait_in_seconds=30)
    print('Finished processing token')

    save_token_data()
    server.send_message_to_all(msg='Start.')






PORT = 6789
HOST = ""
server = WebsocketServer(HOST, PORT)
server.set_fn_new_client(new_client)
server.set_fn_client_left(client_left)
server.set_fn_message_received(new_message)
server.run_forever()