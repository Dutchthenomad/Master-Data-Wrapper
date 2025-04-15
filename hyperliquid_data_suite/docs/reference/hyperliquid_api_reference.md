# HyperLiquid API Reference

## Table of Contents

1. [Introduction](#introduction)
2. [API Notation](#api-notation)
3. [Asset IDs](#asset-ids)
4. [Tick and Lot Size](#tick-and-lot-size)
5. [Nonces and API Wallets](#nonces-and-api-wallets)
6. [Info Endpoint](#info-endpoint)
7. [Exchange Endpoint](#exchange-endpoint)
8. [WebSocket API](#websocket-api)
9. [Authentication](#authentication)

## Introduction

This document provides a comprehensive reference for the HyperLiquid API, which allows developers to interact with the HyperLiquid exchange programmatically. HyperLiquid is a decentralized exchange (DEX) that offers both spot and perpetual futures trading.

**Exchange Information:**
- Website: https://app.hyperliquid.xyz/
- API Docs: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api
- Connection Type: WebSocket

## API Notation

The current v0 API uses some nonstandard notation. Relevant standardization will be batched into a breaking v1 API change.

| Abbreviation | Full name | Explanation |
|-------------|-----------|-------------|
| Px | Price | |
| Sz | Size | In units of coin, i.e. base currency |
| Szi | Signed size | Positive for long, negative for short |
| Ntl | Notional | USD amount, Px * Sz |
| Side | Side of trade or book | B = Bid = Buy, A = Ask = Short. Side is aggressing side for trades. |
| Asset | Asset | An integer representing the asset being traded. See below for explanation |
| Tif | Time in force | GTC = good until canceled, ALO = add liquidity only (post only), IOC = immediate or cancel |

## Asset IDs

When perpetual endpoints expect an integer for asset, use the index of the coin found in the meta info response. E.g. BTC = 0 on mainnet.

For spot endpoints, use 10000 + spotInfo["index"] where spotInfo is the corresponding object in spotMeta that has the desired quote and base tokens. For example, when submitting an order for PURR/USDC, the asset that should be used is 10000 because its asset index in the spot info is 0.

Note that spot ID is different from token ID, and that mainnet and testnet have different asset IDs. For example, for HYPE:

- Mainnet token ID: 150
- Mainnet spot ID: 107
- Testnet token ID: 1105
- Testnet spot ID: 1035

## Tick and Lot Size

Both Price (px) and Size (sz) have a maximum number of decimals that are accepted.

Prices can have up to 5 significant figures, but no more than MAX_DECIMALS - szDecimals decimal places where MAX_DECIMALS is 6 for perps and 8 for spot. Integer prices are always allowed, regardless of the number of significant figures. E.g. 123456.0 is a valid price even though 12345.6 is not.

Sizes are rounded to the szDecimals of that asset. For example, if szDecimals = 3 then 1.001 is a valid size but 1.0001 is not.

szDecimals for an asset is found in the meta response to the info endpoint.

### Perp price examples
- 1234.5 is valid but 1234.56 is not (too many significant figures)
- 0.001234 is valid, but 0.0012345 is not (more than 6 decimal places)
- If szDecimals = 1, 0.01234 is valid but 0.012345 is not (more than 6 - szDecimals decimal places)

### Spot price examples
- 0.0001234 is valid if szDecimals is 0 or 1, but not if szDecimals is greater than 2 (more than 8-2 decimal places).

## Nonces and API Wallets

### Background
A decentralized L1 must prevent replay attacks. When a user signs a USDC transfer transaction, the receiver cannot broadcast it multiple times to drain the sender's wallet. To solve this Ethereum stores a "nonce" for each address, which is a number that starts at 0. Each transaction must use exactly "nonce + 1" to be included.

### API wallets
These are also known as agent wallets in the docs. A master account can approve API wallets to sign on behalf of the master account or any of the sub-accounts.

Note that API wallets are only used to sign. To query the account data associated with a master or sub-account, you must pass in the actual address of that account. A common pitfall is to use the agent wallet which leads to an empty result.

### API wallet pruning
API wallets and their associated nonce state may be pruned in the following cases:

- The wallet is deregistered. This happens to an existing unnamed API Wallet when an ApproveAgent action is sent to register a new unnamed API Wallet. This also happens to an existing named API Wallet when an ApproveAgent action is sent with a matching name.
- The wallet expires.
- The account that registered the agent no longer has funds.

**Important**: for those using API wallets programmatically, it is strongly suggested to not reuse their addresses. Once an agent is deregistered, its used nonce state may be pruned. Generate a new agent wallet on future use to avoid unexpected behavior. For example, previously signed actions can be replayed once the nonce set is pruned.

### Hyperliquid nonces
Ethereum's design does not work for an onchain order book. A market making strategy can send thousands of orders and cancels in a second. Requiring a precise ordering of inclusion on the blockchain will break any strategy.

On Hyperliquid, the 100 highest nonces are stored per address. Every new transaction must have nonce larger than the smallest nonce in this set and also never have been used before. Nonces are tracked per signer, which is the user address if signed with private key of the address, or the agent address if signed with an API wallet.

Nonces must be within 1 day of the unix millisecond timestamp on the block of the transaction.

The following steps may help port over an automated strategy from a centralized exchange:

1. Use a API wallet per trading process. Note that nonces are stored per signer (i.e. private key), so separate subaccounts signed by the same API wallet will share the nonce tracker of the API wallet. It's recommended to use separate API wallets for different subaccounts.
2. In each trading process, have a task that periodically batches order and cancel requests every 0.1 seconds. It is recommended to batch IOC and GTC orders separately from ALO orders because ALO order-only batches are prioritized by the validators.
3. The trading logic tasks send orders and cancels to the batching task.
4. For each batch of orders or cancels, fetch and increment an atomic counter that ensures a unique nonce for the address. The atomic counter can be fast-forwarded to current unix milliseconds if needed.

This structure is robust to out-of-order transactions within 2 seconds, which should be sufficient for an automated strategy geographically near an API server.

### Suggestions for subaccount and vault users
Note that nonces are stored per signer, which is the address of the private key used to sign the transaction. Therefore, it's recommended that each trading process or frontend session use a separate private key for signing. In particular, a single API wallet signing for a user, vault, or subaccount all share the same nonce set.

If users want to use multiple subaccounts in parallel, it would easier to generate two separate API wallets under the master account, and use one API wallet for each subaccount. This avoids collisions between the nonce set used by each subaccount.

## Info Endpoint

The info endpoint is used to fetch information about the exchange and specific users. The different request bodies result in different corresponding response body schemas.

### Pagination
Responses that take a time range will only return 500 elements or distinct blocks of data. To query larger ranges, use the last returned timestamp as the next startTime for pagination.

### Perpetuals vs Spot
The endpoints in this section as well as websocket subscriptions work for both Perpetuals and Spot. For perpetuals coin is the name returned in the meta response. For Spot, coin should be PURR/USDC for PURR, and @{index} e.g. @1 for all other spot tokens where index is the index in the universe field of the spotMeta response.

### User address
To query the account data associated with a master or sub-account, you must pass in the actual address of that account. A common pitfall is to use an agent wallet's address which leads to an empty result.

### Common Info Endpoint Requests

#### Retrieve mids for all coins
```
POST https://api.hyperliquid.xyz/info
```

Headers:
```
Content-Type: application/json
```

Request Body:
```json
{
    "type": "allMids"
}
```

Response:
```json
{
    "APE": "4.33245",
    "ARB": "1.21695"
}
```

#### Retrieve a user's open orders
```
POST https://api.hyperliquid.xyz/info
```

Headers:
```
Content-Type: application/json
```

Request Body:
```json
{
    "type": "openOrders",
    "user": "0x0000000000000000000000000000000000000000"
}
```

Response:
```json
[
    {
        "coin": "BTC",
        "limitPx": "29792.0",
        "oid": 91490942,
        "side": "A",
        "sz": "0.0",
        "timestamp": 1681247412573
    }
]
```

#### L2 book snapshot
```
POST https://api.hyperliquid.xyz/info
```

Headers:
```
Content-Type: application/json
```

Request Body:
```json
{
    "type": "l2Book",
    "coin": "BTC"
}
```

## Authentication

Authentication for the HyperLiquid API is done using Ethereum signatures. To authenticate requests:

1. Create a message to sign based on the request parameters
2. Sign the message using your Ethereum private key
3. Include the signature in your request

This approach ensures secure and verifiable API access.
