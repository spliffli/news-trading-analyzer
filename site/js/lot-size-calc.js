const accountBalanceInput = document.getElementById('account-balance');
const triggers = document.querySelectorAll('.trigger');

function calculateLots() {
  triggers.forEach(trigger => {
    const lotsPer1k = parseFloat(trigger.querySelector('h5:nth-of-type(4) span').textContent);
    const balance = parseFloat(accountBalanceInput.value);
    const lots = (balance / 1000) * lotsPer1k;
    trigger.querySelector('h5:nth-of-type(5) span').textContent = lots.toFixed(2);
  });
}

accountBalanceInput.addEventListener('input', calculateLots);

// Calculate lots on page load
calculateLots();
