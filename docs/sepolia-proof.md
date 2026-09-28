# MyZubsterProof — Ethereum Sepolia Proof

This document records the first MyZubster on-chain proof experiment deployed on the Ethereum Sepolia test network.

## Contract

- Network: Ethereum Sepolia
- Contract: MyZubsterProof
- Contract address: 0xabCF68e97a32eCa503942A563FF16F209ed45d11
- Solidity compiler: v0.8.34+commit.80d5c536
- Optimization: disabled
- Source verification: Etherscan Exact Match
- License: MIT

Contract:
https://sepolia.etherscan.io/address/0xabCF68e97a32eCa503942A563FF16F209ed45d11#code

## Deployment

- Transaction hash: 0x09dddd29aca76c9a425ba9cb45cefb1bfbe203b9628f5f9526e4a281012d4f20
- Block: 11803203
- Timestamp: 1790630820
- UTC time: 2026-09-28 21:27:00 UTC
- Creator: 0x08ae56e99AdB11Df571c437B18620D6c0075d700

Transaction:
https://sepolia.etherscan.io/tx/0x09dddd29aca76c9a425ba9cb45cefb1bfbe203b9628f5f9526e4a281012d4f20

## Knowledge proof

Knowledge Card:
https://www.myzubster.com/knowledge-card?id=6abaaefb3a7460c4574a45fd

SHA-256 / bytes32 stored on-chain:

0x15b21c4f189259f143f6c946ac866001d88f5bc7aa371cac7cbcc1ce66b43685

The value was verified through Etherscan Read Contract and matches the knowledgeHash stored by MyZubsterProof.

The creator value read from the contract is:

0x08ae56e99AdB11Df571c437B18620D6c0075d700

The timestamp value read from the contract is:

1790630820

## Important scope note

This first experiment anchors the SHA-256 hash of the Knowledge Card URL string.

It does NOT yet hash or prove the complete contents of the Knowledge Card. A future version can canonicalize the card data and anchor a content hash so that changes to the card contents can be detected independently.

## Source

The Solidity source used for this deployment is stored in:

contracts/MyZubsterProof.sol
