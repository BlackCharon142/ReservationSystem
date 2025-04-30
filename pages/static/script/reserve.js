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

document.querySelectorAll('.counter').forEach(initCounter);

/*document.getElementById('add-counter').addEventListener('click', () => {
    const newCounter = document.createElement('div');
    newCounter.className = 'counter';
    newCounter.setAttribute('data-min', '0');
    newCounter.setAttribute('data-max', '20');
    newCounter.innerHTML = `
        <button class="decrement">-</button>
        <div class="number">0</div>
        <button class="increment">+</button>
    `;
    document.getElementById('counters-container').appendChild(newCounter);
    initCounter(newCounter); // Initialize the new counter
});*/