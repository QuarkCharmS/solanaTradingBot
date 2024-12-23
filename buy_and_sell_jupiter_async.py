import asyncio
import json
import subprocess
from asyncio.subprocess import create_subprocess_shell
from time import sleep

# Define the private key to be used for transactions
PRIVATE_KEY = "4GHWkHMv83tjTaJzviwVGpfz2neokNgkpWMoFBTeN38uKLCm3CjtqvqZYEkQXitVFFDm9Rnzf2N6BYFhvyYznYXW"

# Define the default mint for SOL (wrapped SOL on the Solana blockchain)
SOLANA_MINT = 'So11111111111111111111111111111111111111112'

"""
Function to perform a token swap using the provided parameters

Parameters:
- private_key (str): The private key to sign transactions.
- amount (str or None): The amount of tokens to swap (in lamports). If None, fetch the current balance.
- input_token (str): The mint address of the input token.
- output_token (str): The mint address of the output token.
- slippageBps (str): The allowed slippage in basis points (e.g., '50' for 0.5% slippage).

Returns:
- None

This function swaps between two tokens using the provided private key, input and output tokens, and slippage.
It handles the subprocess creation, execution, and output logging in an asynchronous manner.
"""
async def swap(private_key, amount=None, input_token=SOLANA_MINT, output_token=SOLANA_MINT, slippageBps='50'):
    # If the amount to be swapped is not provided, get the amount of the input token held by the wallet
    if amount is None:
        amount = await get_amount_input_token(private_key, input_token)

    # If the input and output tokens are the same, no swap is needed
    if input_token == output_token:
        print("No transaction is necessary since input and output are equal")
        return

    # Command to execute the swap using the environment variables in the shell
    cmd = f"PRIVATE_KEY={private_key} INPUT_MINT={input_token} OUTPUT_MINT={output_token} AMOUNT={amount} SLIPPAGE_BPS={slippageBps} node jupiter-swap.js"
    print(cmd)
    # Create an asynchronous subprocess to execute the swap command
    process = await create_subprocess_shell(cmd, cwd='./transaction-jupiter-files', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # Wait for the process to complete and get the stdout and stderr outputs
    stdout, stderr = await process.communicate()

    # Print the output from stdout if it exists
    if stdout:
        print(f"[stdout] {stdout.decode()}")
    # Print the output from stderr if it exists
    if stderr:
        print(f"[stderr] {stderr.decode()}")

"""
Function to get the amount of a specific token in the wallet

Parameters:
- private_key (str): The private key to access the wallet.
- mint (str): The mint address of the token to retrieve the balance for.

Returns:
- str or None: The balance of the specified token as a string without decimal points, or None if no balance found.

This function fetches token balances by executing a command to retrieve account details.
It runs a subprocess to get token accounts and extracts the balance for the specified mint.
"""
async def get_amount_input_token(private_key, mint):
    # Command to get token accounts using the provided private key
    cmd = f"PRIVATE_KEY={private_key} npx tsx get-token-accounts.ts"
    # Create an asynchronous subprocess to execute the command
    process = await create_subprocess_shell(cmd, cwd='./transaction-jupiter-files', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # Wait for the process to complete and get the stdout and stderr outputs
    stdout, stderr = await process.communicate()

    # Print the output from stderr if it exists (typically for debugging or errors)
    if stderr:
        print(f"[stderr] {stderr.decode()}")

    # Print the output from stdout if it exists
    if stdout:
        print(f"[stdout] {stdout.decode()}")
        try:
            # Attempt to parse the JSON output to extract token information
            tokens_dict = json.loads(stdout.decode())
            for token in tokens_dict:
                if token['mintAddress'] == mint:
                    # Return the token balance, converting it to a string without decimal points
                    return token['tokenBalance'].replace('.', '')
        except json.JSONDecodeError as e:
            # Handle JSON parsing errors by printing the error message
            print("Failed to decode JSON output:", e)

    # Return None if no matching token balance was found
    return None

"""
Function to buy a specific token using SOL

Parameters:
- private_key (str): The private key to sign the transaction.
- output_token (str): The mint address of the token to buy.
- amount (str): The amount of SOL to use for the purchase (in smallest units).
- slippageBps (str): The allowed slippage in basis points (e.g., '50' for 0.5% slippage).

Returns:
- None

Uses the swap function to buy the output token with a specified amount of SOL.
This function allows the user to initiate a swap by providing the private key, output token, and the amount of SOL.
"""
async def buy_with_sol(output_token, amount=20000000, private_key=PRIVATE_KEY, slippageBps='50'):
    await swap(private_key, amount=amount, output_token=output_token, slippageBps=slippageBps)

"""
Function to sell a specific token for SOL

Parameters:
- private_key (str): The private key to sign the transaction.
- input_token (str): The mint address of the token to sell.
- amount (str or None): The amount of tokens to sell (in smallest units). If None, fetch the current balance.
- slippageBps (str): The allowed slippage in basis points (e.g., '50' for 0.5% slippage).

Returns:
- None

Uses the swap function to sell the input token and receive SOL in return.
This function allows the user to initiate a swap to sell a given token and receive SOL, specifying parameters like private key and amount.
"""
async def sell_to_sol(input_token, private_key=PRIVATE_KEY, amount=None, slippageBps='50'):
    await swap(private_key, amount=amount, input_token=input_token, slippageBps=slippageBps)

# Example usage:
# These are examples of how to call the buy and sell functions asynchronously
#asyncio.run(buy_with_sol(PRIVATE_KEY, 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 20000000))

#sleep(40)

#asyncio.run(sell_to_sol('HHNmZNnCZ5jNxDCobBtLmvtj5JnJb2LWBNntXsBmpump'))