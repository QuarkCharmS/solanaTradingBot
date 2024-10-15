import { Connection, PublicKey } from '@solana/web3.js';
import { programs } from '@metaplex/js';
import fetch from 'node-fetch';

import * as Raydium from '@raydium-io/raydium-sdk';

// Connect to the Solana cluster
const connection = new Connection('https://api.mainnet-beta.solana.com');

// Get the token address
const tokenAddress = process.argv[2];

if (!tokenAddress) {
  console.error('Token address is required as a command-line argument.');
  process.exit(1);
}

// Define the public key of the token metadata account
const tokenMintAddress = new PublicKey(tokenAddress);

async function fetchMetadata() {
  try {
    const metadataPDA = await programs.metadata.Metadata.getPDA(tokenMintAddress);
    const metadataAccount = await programs.metadata.Metadata.load(connection, metadataPDA);
    const metadataUri = metadataAccount.data.data.uri;

    console.log('Metadata URI:', metadataUri);

    const response = await fetch(metadataUri);
    const metadataJson = await response.json();

    console.log('Metadata JSON:', metadataJson);

    // Extract social media links
    const socialMediaLinks = metadataJson.attributes?.filter(
      (attribute: { trait_type: string }) => attribute.trait_type === 'Social Media'
    ).map((attribute: { value: string }) => attribute.value);

    console.log('Social Media Links:', socialMediaLinks);

    // Check liquidity status (hypothetical example)
    const liquidityStatus = await checkLiquidityLockStatus(tokenMintAddress);
    console.log('Liquidity Locked:', liquidityStatus.locked);
    console.log('Lock Details:', liquidityStatus.details);

  } catch (error) {
    console.error('Error fetching metadata:', error);
  }
}

async function checkLiquidityLockStatus(tokenMintAddress: PublicKey) {
  // Hypothetical function to check liquidity lock status
  // This would depend on the specific DeFi platform's SDK or API
  try {
    const poolInfo = await Raydium.getLiquidityPoolInfo(tokenMintAddress.toBase58());

    return {
      locked: poolInfo.locked, // Boolean indicating if liquidity is locked
      details: poolInfo.lockDetails // Details about the lock (duration, amount, etc.)
    };
  } catch (error) {
    console.error('Error checking liquidity lock status:', error);
    return {
      locked: false,
      details: 'Unable to determine liquidity lock status'
    };
  }
}

fetchMetadata();

