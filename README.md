# SPL Airdrop Wallet Scanner (Web UI)

Simple static webpage you can run in VS Code to:

1. Generate new Solana wallets.
2. Scan balances for a specific SPL token mint.
3. Export wallet + balance results to JSON.

## Run locally

From this folder:

```bash
python3 -m http.server 8080
```

Open `http://localhost:8080` in your browser.

## Notes

- Uses browser-loaded `@solana/web3.js` and `bs58` from CDNs.
- Token balance scan uses `getParsedTokenAccountsByOwner` filtered by mint.
- Keep generated secret keys secure and never share them publicly.
