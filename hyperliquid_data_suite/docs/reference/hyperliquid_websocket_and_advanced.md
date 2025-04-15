# HyperLiquid WebSocket and Advanced API Features

## Table of Contents

1. [WebSocket Post Requests](#websocket-post-requests)
2. [Timeouts and Heartbeats](#timeouts-and-heartbeats)
3. [Error Responses](#error-responses)
4. [Rate Limits](#rate-limits)
5. [Bridge2 Integration](#bridge2-integration)
6. [Deploying HIP-1 and HIP-2 Assets](#deploying-hip-1-and-hip-2-assets)

## WebSocket Post Requests

The WebSocket API supports posting requests that you can normally post through the HTTP API. These requests are either info requests or signed actions.

### Request Format

To send a payload via the WebSocket API, you must wrap it as follows:

```json
{
  "method": "post",
  "id": <number>,
  "request": {
    "type": "info" | "action",
    "payload": { ... }
  }
}
```

**Note**: 
- The `method` and `id` fields are mandatory. 
- It is recommended that you use a unique id for every post request you send in order to track outstanding requests through the channel.
- Explorer requests are not supported via WebSocket.

### Response Format

The server will respond to post requests with either a success or an error. For errors, a String is returned mirroring the HTTP status code and description that would have been returned if the request were sent through HTTP.

```json
{
  "channel": "post",
  "data": {
    "id": <number>,
    "response": {
      "type": "info" | "action" | "error",
      "payload": { ... }
    }
  }
}
```

### Examples

#### Sending an L2Book Info Request

```json
{
  "method": "post",
  "id": 123,
  "request": {
    "type": "info",
    "payload": {
      "type": "l2Book",
      "coin": "ETH",
      "nSigFigs": 5,
      "mantissa": null
    }
  }
}
```

Sample response:

```json
{
  "channel": "post",
  "data": {
    "id": <number>,
    "response": {
      "type": "info",
      "payload": {
        "type": "l2Book",
        "data": {
          "coin": "ETH",
          "time": <number>,
          "levels": [
            [{"px":"3007.1","sz":"2.7954","n":1}],
            [{"px":"3040.1","sz":"3.9499","n":1}]
          ]
        }
      }
    }
  }
}
```

#### Sending an Order Signed Action Request

```json
{
  "method": "post",
  "id": 256,
  "request": {
    "type": "action",
    "payload": {
      "action": {
        "type": "order",
        "orders": [{"a": 4, "b": true, "p": "1100", "s": "0.2", "r": false, "t": {"limit": {"tif": "Gtc"}}}],
        "grouping": "na"
      },
      "nonce": 1713825891591,
      "signature": {
        "r": "...",
        "s": "...",
        "v": "..."
      },
      "vaultAddress": "0x12...3"
    }
  }
}
```

Sample response:

```json
{
  "channel": "post",
  "data": {
    "id": 256,
    "response": {
      "type":"action",
      "payload": {
        "status": "ok",
        "response": {
          "type": "order",
          "data": {
            "statuses": [
              {
                "resting": {
                  "oid": 88383,
                }
              }
            ]
          }
        }
      }
    }
  }
}
```

## Timeouts and Heartbeats

The server will close any connection if it hasn't sent a message to it in the last 60 seconds. If you are subscribing to a channel that doesn't receive messages every 60 seconds, you can send heartbeat messages to keep your connection alive.

### Heartbeat Format

Client request:
```json
{ "method": "ping" }
```

Server response:
```json
{ "channel": "pong" }
```

## Error Responses

Order and cancel errors are usually returned as a vector with the same length as the batched request.

### Common Error Types

| Error Source | Error Type | Error String |
|--------------|------------|---------------|
| Order | Tick | Price must be divisible by tick size. |
| Order | MinTradeNtl | Order must have minimum value of $10 |
| Order | Margin | Insufficient margin to place order. |
| Order | ReduceOnly | Reduce only order would increase position. |
| Order | BadAloPx | Post only order would have immediately matched, bbo was {bbo}. |
| Order | IocCancel | Order could not immediately match against any resting orders. |
| Order | BadTriggerPx | Invalid TP/SL price. |
| Order | MarketOrderNoLiquidity | No liquidity available for market order. |
| Cancel | MissingOrder | Order was never placed, already canceled, or filled. |

**Important**: Some errors are a deterministic function of the payload itself, and these are instead returned earlier as part of pre-validation. In this case, only one error is returned for the entire payload, as some of these errors do not apply to a specific order or cancel.

Examples include: empty batch of orders, non-reduce-only TP/SL orders, and some forms of tick size validation.

For API users that use batching, it's recommended to handle the case where a single error is returned for a batch of multiple orders. In this case, the response could be duplicated n times before being sent to the callback function, as the whole batch was rejected for this same reason.

## Rate Limits

The following rate limits apply per IP address:

- REST requests share an aggregated weight limit of 1200 per minute.
- All documented exchange API requests have a weight of 1 + floor(batch_length / 40). For example, unbatched actions have weight 1 and a batched order request of length 79 has weight 2. Here, batch_length is the length of the array in the action, e.g., the number of orders in a batched order action.
- The following info requests have weight 2: l2Book, allMids, clearinghouseState, orderStatus, spotClearinghouseState, exchangeStatus.
- The following info requests have weight 60: userRole.
- All other documented info requests have weight 20.

## Bridge2 Integration

HyperLiquid Bridge2 allows for deposits and withdrawals between Ethereum and HyperLiquid. The following examples show how to integrate with Bridge2.

### Deposit Flow

1. User approves USDC for the Bridge2 contract on Ethereum
2. User calls the deposit function on the Bridge2 contract
3. Bridge2 transfers USDC from the user to itself
4. After confirmation on Ethereum, the deposit is credited on HyperLiquid

### Withdrawal Flow

1. User signs a withdrawal request on HyperLiquid
2. The withdrawal is processed on HyperLiquid
3. After confirmation on HyperLiquid, the withdrawal is processed on Ethereum
4. Bridge2 transfers USDC from itself to the user

### Example Withdrawal Request

```json
{
    "action": {
        "type": "withdraw3",
        "signatureChainId": "0xa4b1",
        "hyperliquidChain": "Mainnet",
        "amount": "100.0",
        "destination": "0x1234567890123456789012345678901234567890"
    },
    "nonce": 1713825891591,
    "signature": {
        "r": "...",
        "s": "...",
        "v": "..."
    },
    "vaultAddress": "0x1234567890123456789012345678901234567890"
}
```

## Deploying HIP-1 and HIP-2 Assets

HyperLiquid Improvement Proposals (HIPs) define standards for deploying new assets on HyperLiquid.

### HIP-1: Perpetual Futures

HIP-1 defines the standard for deploying perpetual futures contracts on HyperLiquid. The key parameters include:

- Asset name and symbol
- Initial price
- Funding rate parameters
- Liquidation parameters
- Trading fee parameters

### HIP-2: Spot Markets

HIP-2 defines the standard for deploying spot markets on HyperLiquid. The key parameters include:

- Base token name and symbol
- Quote token (usually USDC)
- Initial price
- Trading fee parameters

### Deployment Process

1. Submit a proposal through the HyperLiquid governance process
2. Community votes on the proposal
3. If approved, the HyperLiquid team deploys the asset
4. The asset becomes available for trading
