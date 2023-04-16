const excludeNotTradedCheckbox = document.getElementById('exclude-not-traded');
const cardWrappers = document.querySelectorAll('.card-wrapper');

function toggleNotTradedCards() {
  cardWrappers.forEach(wrapper => {
    const card = wrapper.querySelector('.card');
    if (excludeNotTradedCheckbox.checked && card.classList.contains('not-trading')) {
      wrapper.style.display = 'none';
    } else {
      wrapper.style.display = '';
    }
  });
}

excludeNotTradedCheckbox.addEventListener('change', toggleNotTradedCards);

// Hide not-trading cards on page load if the checkbox is checked
toggleNotTradedCards();
