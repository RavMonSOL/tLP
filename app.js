const rpcInput = document.getElementById('rpc');
const mintInput = document.getElementById('mint');
const countInput = document.getElementById('count');
const generateBtn = document.getElementById('generate');
const scanBtn = document.getElementById('scan');
const downloadBtn = document.getElementById('download');
const statusEl = document.getElementById('status');
const rowsEl = document.getElementById('rows');

/** @type {{index:number, pubkey:string, secretKey:string, balance:number|null, error?:string}[]} */
let wallets = [];

const setStatus = (text) => {
  statusEl.textContent = text;
};

const renderRows = () => {
  rowsEl.innerHTML = '';
  for (const wallet of wallets) {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${wallet.index}</td>
      <td>${wallet.pubkey}</td>
      <td>${wallet.balance === null ? '-' : wallet.balance}</td>
      <td>
        <div>${wallet.secretKey}</div>
        ${wallet.error ? `<div class="small">Error: ${wallet.error}</div>` : ''}
      </td>
    `;
    rowsEl.appendChild(tr);
  }
};

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

generateBtn.addEventListener('click', async () => {
  const count = Number.parseInt(countInput.value, 10);
  if (!Number.isInteger(count) || count < 1 || count > 500) {
    alert('Wallet count must be 1-500.');
    return;
  }

  wallets = [];
  for (let i = 0; i < count; i += 1) {
    const keypair = solanaWeb3.Keypair.generate();
    wallets.push({
      index: i + 1,
      pubkey: keypair.publicKey.toBase58(),
      secretKey: bs58.encode(keypair.secretKey),
      balance: null,
    });
  }

  renderRows();
  setStatus(`Generated ${wallets.length} wallets. Ready to scan token balances.`);
  scanBtn.disabled = false;
  downloadBtn.disabled = false;
});

scanBtn.addEventListener('click', async () => {
  if (!wallets.length) {
    return;
  }

  const rpc = rpcInput.value.trim();
  const mint = mintInput.value.trim();

  if (!rpc) {
    alert('RPC endpoint is required.');
    return;
  }

  if (!mint) {
    alert('Token mint is required.');
    return;
  }

  const connection = new solanaWeb3.Connection(rpc, 'confirmed');
  const mintKey = new solanaWeb3.PublicKey(mint);
  setStatus('Scanning wallets...');
  scanBtn.disabled = true;

  let completed = 0;
  for (const wallet of wallets) {
    try {
      const owner = new solanaWeb3.PublicKey(wallet.pubkey);
      const response = await connection.getParsedTokenAccountsByOwner(owner, { mint: mintKey });

      let total = 0;
      for (const account of response.value) {
        const amount = account.account.data.parsed.info.tokenAmount.uiAmount || 0;
        total += amount;
      }

      wallet.balance = total;
      wallet.error = undefined;
    } catch (error) {
      wallet.balance = 0;
      wallet.error = error instanceof Error ? error.message : String(error);
    }

    completed += 1;
    setStatus(`Scanned ${completed}/${wallets.length} wallets...`);
    renderRows();
    await sleep(120);
  }

  const sum = wallets.reduce((acc, wallet) => acc + (wallet.balance || 0), 0);
  setStatus(`Done. Total token balance found: ${sum}`);
  scanBtn.disabled = false;
});

downloadBtn.addEventListener('click', () => {
  if (!wallets.length) {
    return;
  }

  const payload = {
    generatedAt: new Date().toISOString(),
    rpc: rpcInput.value.trim(),
    mint: mintInput.value.trim(),
    wallets,
  };

  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = 'wallet-scan-results.json';
  link.click();
  URL.revokeObjectURL(link.href);
});
