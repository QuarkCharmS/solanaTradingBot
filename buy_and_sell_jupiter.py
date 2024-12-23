from subprocess import run as exec_code
import json
import time

'''
const inputMint = process.env.INPUT_MINT || 'So11111111111111111111111111111111111111112';
const outputMint = process.env.OUTPUT_MINT || 'So11111111111111111111111111111111111111112';
const amount = process.env.AMOUNT || '';
const slippageBps = process.env.SLIPPAGE_BPS || '50';
'''
import time

PRIVATE_KEY="4GHWkHMv83tjTaJzviwVGpfz2neokNgkpWMoFBTeN38uKLCm3CjtqvqZYEkQXitVFFDm9Rnzf2N6BYFhvyYznYXW"

SOLANA_MINT = 'So11111111111111111111111111111111111111112'

def swap(private_key, amount=None, input_token=SOLANA_MINT, output_token=SOLANA_MINT, slippageBps='50'):

    if amount == None:
        amount = get_amount_input_token(private_key, input_token)

    if input_token == output_token:
        print("No transaction is necessary since input and output are equal")
        return

    swap_result = exec_code(f"PRIVATE_KEY={private_key} INPUT_MINT={input_token} OUTPUT_MINT={output_token} AMOUNT={amount} SLIPPAGE_BPS={slippageBps} node jupiter-swap.js",
              cwd='./transaction-jupiter-files',
              shell=True,
              capture_output=True,
              text=True)

    print(swap_result)

def get_amount_input_token(private_key, mint):
    token_json = exec_code(f"PRIVATE_KEY={private_key} npx tsx get-token-accounts.ts",
                            cwd='./transaction-jupiter-files',
                            capture_output=True,
                            shell=True,
                            text=True)

    print(token_json.stdout)

    tokens_dict = json.loads(str(token_json.stdout))

    for token in tokens_dict:
        if token['mintAddress'] == mint:
            return token['tokenBalance'].replace('.', '')


def buy_with_sol(private_key, output_token, amount, slippageBps='50'):
    swap(private_key,
         amount=amount,
         output_token=output_token,
         slippageBps=slippageBps)


def sell_to_sol(private_key, input_token, amount=None, slippageBps='50'):
    swap(private_key,
         amount=amount,
         input_token=input_token,
         slippageBps=slippageBps)

token_to_test='DdVo41jyM382Zk3mCmiz6iFz89ibb32WjrSvADxepump'

buy_with_sol(PRIVATE_KEY, token_to_test, 20000000)

time.sleep(40)

sell_to_sol(PRIVATE_KEY, token_to_test)
