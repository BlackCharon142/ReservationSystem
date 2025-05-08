function updateWalletBalance() {
  fetch("/ajax/wallet-balance/")
    .then(res => res.json())
    .then(data => {
      const el = document.querySelector('.wallet-balance');
      if (!el) return;
      // use the pre-formatted string for thousand-separators
      el.textContent = data.formatted;
    })
    .catch(err => console.error('Failed to fetch wallet balance:', err));
}

document.addEventListener('walletBalanceRefresh', updateWalletBalance);