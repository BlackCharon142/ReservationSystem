function initCounter(counter) {
    const minValue = parseInt(counter.getAttribute('data-min'), 10);
    const maxValue = parseInt(counter.getAttribute('data-max'), 10);
    let currentValue = minValue;

    const counterValueElement = counter.querySelector('.number');
    const incrementButton = counter.querySelector('.increment');
    const decrementButton = counter.querySelector('.decrement');

    incrementButton.addEventListener('click', () => {
        if (currentValue < maxValue) {
            currentValue++;
            updateCounter();
        }
    });

    decrementButton.addEventListener('click', () => {
        if (currentValue > minValue) {
            currentValue--;
            updateCounter();
        }
    });

    function updateCounter() {
        counterValueElement.textContent = currentValue;
    }
}

function updateCounters(){
    document.querySelectorAll('.counter').forEach(initCounter);
}

updateCounters();