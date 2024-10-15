import { Connection, GetProgramAccountsFilter, Keypair } from "@solana/web3.js";
import { TOKEN_PROGRAM_ID } from "@solana/spl-token";
import { Wallet } from '@project-serum/anchor';
import bs58 from 'bs58';


//https://warmhearted-frequent-grass.solana-mainnet.quiknode.pro/65c2898b9eaf8bbd73d1954c7ce8dc2bdf0d62fe



const rpcEndpoint = 'https://warmhearted-frequent-grass.solana-mainnet.quiknode.pro/65c2898b9eaf8bbd73d1954c7ce8dc2bdf0d62fe';
const solanaConnection = new Connection(rpcEndpoint);
//FtGB8BtiRQkVn67JiN5rk2WbjHDULRdt23h63oxtuakU

const wallet = new Wallet(Keypair.fromSecretKey(bs58.decode(process.env.PRIVATE_KEY || '')));
const walletToQuery = wallet.publicKey.toString();
//const walletToQuery = process.env.PUBLIC_KEY || '';

async function getTokenAccounts(wallet: string, solanaConnection: Connection) {
  
  const filters: GetProgramAccountsFilter[] = [
    {
      dataSize: 165,    //size of account (bytes)
    },
    {
      memcmp: {
        offset: 32,     //location of our query in the account (bytes)
        bytes: wallet,  //our search criteria, a base58 encoded string
      }            
    }
  ];

  const accounts = await solanaConnection.getParsedProgramAccounts(
    TOKEN_PROGRAM_ID,   //SPL Token Program, new PublicKey("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
    {filters: filters}
  );

  //console.log(`Found ${accounts.length} token account(s) for wallet ${wallet}.`);
  
  const results: Array<{
    tokenAccount: string,
    mintAddress: string,
    tokenBalance: string
  }> = [];

  accounts.forEach((account) => {
    //Parse the account data
    const parsedAccountInfo:any = account.account.data;
    const mintAddress:string = parsedAccountInfo["parsed"]["info"]["mint"];
    const tokenBalance: number = parsedAccountInfo["parsed"]["info"]["tokenAmount"]["uiAmount"];
    //Log results
    //console.log(`Token Account No. ${i + 1}: ${account.pubkey.toString()}`);
    //console.log(`--Token Mint: ${mintAddress}`);
    //console.log(`--Token Balance: ${tokenBalance}`);

    results.push({
      tokenAccount: account.pubkey.toString(),
      mintAddress: mintAddress,
      tokenBalance: tokenBalance.toString()
    })
  });

  console.log(JSON.stringify(results, null, 2));
}

getTokenAccounts(walletToQuery,solanaConnection);
