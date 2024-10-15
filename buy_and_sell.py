from raydium import buy_token, sell_token
from solana.rpc.api import Client, Keypair
from solana.rpc.async_api import AsyncClient
import time

RPC = "https://warmhearted-frequent-grass.solana-mainnet.quiknode.pro/65c2898b9eaf8bbd73d1954c7ce8dc2bdf0d62fe/"
async_solana_client = AsyncClient(RPC)
solana_client = Client(RPC)

SOLANA_MINT = 'So11111111111111111111111111111111111111112'


def buy_token_in_raydium(token):
    time_start = time.time()
    key = open('keypair.txt').read().strip()
    keypair = Keypair.from_base58_string(key)

    amount = 0.01

    buy_tx = buy_token(
        solana_client,
        async_solana_client,
        token,
        keypair,
        amount=amount,
        compute_unit_price=300000,
        compute_unit_limit=695361,
        debug=True
    )

    print(f"[+] [{key[:6]}] Bought {amount} SOL of {token}: https://solscan.io/tx/{buy_tx}")
    time_end = time.time()
    print(f'total time = {time_end - time_start}')


def sell_token_in_raydium(token):
    time_start = time.time()
    key = open('keypair.txt').read().strip()
    keypair = Keypair.from_base58_string(key)

    sell_tx = sell_token(
        solana_client,
        async_solana_client,
        token,
        keypair,
        None, #None can be used to sell everything
        compute_unit_price=695361,
        compute_unit_limit=1050000,
        debug=True
    )

    print(f"[+] [{key[:6]}] Sold {token}: https://solscan.io/tx/{sell_tx}")
    time_end = time.time()
    print(f'total time = {time_end - time_start}')

