# Hyperliquid Official Documentation Reference

This folder contains a local copy of the official Hyperliquid API documentation for offline reference. These documents are essential for understanding the Hyperliquid API endpoints, parameters, and response formats as the suite evolves.

## Documentation Files

1. **[Hyperliquid API Reference](hyperliquid_api_reference.md)**
   - Complete reference of all API endpoints, parameters, and response formats
   - Detailed explanations of asset IDs, tick sizes, and nonce management
   - Authentication requirements and methods

2. **[Hyperliquid Implementation Guide](hyperliquid_implementation_guide.md)**
   - Practical code examples for implementing the connector
   - Market data retrieval patterns
   - Order execution and account management
   - Common issues and solutions

3. **[WebSocket and Advanced Features](hyperliquid_websocket_and_advanced.md)**
   - WebSocket API implementation details
   - Rate limiting information
   - Bridge2 integration for deposits and withdrawals
   - Asset deployment information

## Usage

- Refer to these documents when adding new endpoints to `HyperliquidClient`
- Check for updates in the official Hyperliquid documentation online and refresh this local copy as needed
- Use the implementation examples when extending the suite's functionality

## Important Notes

- Always follow the official Hyperliquid protocols exactly as specified
- Pay special attention to nonce management and signature generation when implementing trading functionality
- When implementing WebSocket connections, remember to implement heartbeats
- For production systems, implement proper error handling and rate limit management

## Official Resources

- [Hyperliquid Official Documentation](https://hyperliquid.gitbook.io/hyperliquid-docs/)
- [Hyperliquid Exchange](https://app.hyperliquid.xyz/)
- [Hyperliquid GitHub](https://github.com/hyperliquid-dex/)
