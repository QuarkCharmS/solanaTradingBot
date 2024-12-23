import { Connection, Keypair, VersionedTransaction } from '@solana/web3.js';
import fetch from 'cross-fetch';
import { Wallet } from '@project-serum/anchor';
import bs58 from 'bs58';
import { ComputeBudgetProgram, TransactionMessage } from '@solana/web3.js'; // Ensure this import is at the top


const connection = new Connection('https://warmhearted-wider-dust.solana-mainnet.quiknode.pro/bbc478ea66833e371dd5590476befc2569394c88');

const wallet = new Wallet(Keypair.fromSecretKey(bs58.decode(process.env.PRIVATE_KEY || '')));
const inputMint = process.env.INPUT_MINT || 'So11111111111111111111111111111111111111112';
const outputMint = process.env.OUTPUT_MINT || 'So11111111111111111111111111111111111111112';
const amount = process.env.AMOUNT || '';
const slippageBps = process.env.SLIPPAGE_BPS || '50';
const priorityRate = process.env.PRIORITY_RATE || '0';


// EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v

// Swapping SOL to USDC with input 0.1 SOL and 0.5% slippage
const quoteResponse = await (
  await fetch(`https://quote-api.jup.ag/v6/quote?inputMint=${inputMint}\
&outputMint=${outputMint}\
&amount=${amount}\
&slippageBps=${slippageBps}`
  )
).json();
// console.log({ quoteResponse })
console.log("##### Path: ")
console.log({ quoteResponse })

// get serialized transactions for the swap
const { swapTransaction } = await (
  await fetch('https://quote-api.jup.ag/v6/swap', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      // quoteResponse from /quote api
      quoteResponse,
      // user public key to be used for the swap
      userPublicKey: wallet.publicKey.toString(),
      // auto wrap and unwrap SOL. default is true
      wrapAndUnwrapSol: true,
      // feeAccount is optional. Use if you want to charge a fee.  feeBps must have been passed in /quote API.
      // feeAccount: "fee_account_public_key"
    })
  })
).json();

console.log("##### Serialized Swap Transaction:")
console.log({ swapTransaction })

// deserialize the transaction
const swapTransactionBuf = Buffer.from(swapTransaction, 'base64');
var transaction = VersionedTransaction.deserialize(swapTransactionBuf);
console.log(transaction);


//###############################################################
//
//
//
const addPriorityFee = ComputeBudgetProgram.setComputeUnitPrice({
    microLamports: priorityRate
});

const message = TransactionMessage.decompile(transaction.message);

// Insert the priority fee instruction at the beginning or appropriate position
message.instructions.unshift(addPriorityFee);

transaction.message = message.compileToV0Message();

//###############################################################

// sign the transaction
transaction.sign([wallet.payer]);

console.log("##### Transaction signed:")
console.log({ transaction })


// get the latest block hash
const latestBlockHash = await connection.getLatestBlockhash();

// Execute the transaction
const rawTransaction = transaction.serialize()
const txid = await connection.sendRawTransaction(rawTransaction, {
  skipPreflight: true,
  maxRetries: 2
});
await connection.confirmTransaction({
 blockhash: latestBlockHash.blockhash,
 lastValidBlockHeight: latestBlockHash.lastValidBlockHeight,
 signature: txid
});
console.log(`https://solscan.io/tx/${txid}`);
