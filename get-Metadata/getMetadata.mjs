// filename: fetchMetadata.mjs
import { Connection, PublicKey } from '@solana/web3.js';
import { programs } from '@metaplex/js';
import fetch from 'node-fetch';


// Connect to the Solana cluster
const connection = new Connection('https://api.mainnet-beta.solana.com');

// Get the token address
const token_address = process.argv[2];

// Define the public key of the token metadata account
const tokenMintAddress = new PublicKey(token_address);

async function fetchMetadata() {
  try {
    const metadataPDA = await programs.metadata.Metadata.getPDA(tokenMintAddress);
    const metadataAccount = await programs.metadata.Metadata.load(connection, metadataPDA);
    const metadataUri = metadataAccount.data.data.uri;

    console.log(String(metadataUri));

    const response = await fetch(metadataUri);
    const metadataJson = await response.json();

    //console.log(metadataJson);

    // Extract social media links
    const socialMediaLinks = metadataJson.attributes?.filter(
      attribute => attribute.trait_type === 'Social Media'
    ).map(attribute => attribute.value);


  } catch (error) {
    console.error('Error fetching metadata:', error);
  }
}


fetchMetadata();
