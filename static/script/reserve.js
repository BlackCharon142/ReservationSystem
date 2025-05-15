function initCounter(counter) {
    const minValue = parseInt(counter.dataset.min, 10);
    const maxValue = parseInt(counter.dataset.max, 10);
    // NEW: read data-current, fall back to min
    let currentValue = parseInt(counter.dataset.current, 10);
    if (isNaN(currentValue)) currentValue = minValue;

    const counterValueElement = counter.querySelector('.number');
    const incrementButton    = counter.querySelector('.increment');
    const decrementButton    = counter.querySelector('.decrement');
    const menuId             = counter.closest('.date-meal-row').dataset.mealId;

    // Ensure the display matches
    counterValueElement.textContent = currentValue;

    incrementButton.addEventListener('click', () => {
        if (currentValue >= maxValue) return;
        fetch("/ajax/reserve/", {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: `menu_id=${menuId}`
        })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                currentValue++;
                counterValueElement.textContent = currentValue;
                counter.dataset.current = currentValue;
                document.dispatchEvent(new Event('walletBalanceRefresh'));
            } else {
                alert(data.error);
            }
        });
    });

    decrementButton.addEventListener('click', () => {
        if (currentValue <= minValue) return;
        fetch("/ajax/cancel/", {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: `menu_id=${menuId}`
        })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                currentValue--;
                counterValueElement.textContent = currentValue;
                counter.dataset.current = currentValue;
                document.dispatchEvent(new Event('walletBalanceRefresh'));
                fetchMealsForDate($('#myDate').attr('data-timestamp'))
            } else {
                alert(data.error);
            }
        });
    });
}

function updateCounters(){
    document.querySelectorAll('.counter').forEach(initCounter);
}

        function fetchMealsForDate(timestamp) {
            fetch(`/ajax/get-meals/?timestamp=${timestamp}`)
                .then(res => res.json())
                .then(data => {
                    if (data.meals) {
                        updateMealTable(data.meals);
                    } else {
                        updateMealTable([]);
                        console.error(data.error || 'No meals found');
                    }
                })
                .catch(err => console.error('AJAX error:', err));
        }

        function updateMealTable(meals) {
          const tbody = document.querySelector('.date-meal-menu tbody');
          tbody.innerHTML = ''; // clear old rows

          meals.forEach(item => {
            const tr = document.createElement('tr');
            tr.className = 'date-meal-row';
            tr.dataset.mealId = item.id;

            let html = `
              <td><img src="${item.image_url}" /></td>
              <td class="date-meal-name">${item.name}</td>
              <td class="date-meal-description">${item.description}</td>
              <td class="date-meal-type">${item.type}</td>
              <td class="date-meal-price">${item.price.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",")} <span>تومان</span></td>
              <td>`;

            if (item.max_qty > 0) {
              // subtract already reserved from remaining stock?
              // if you want `max` to be "how many more they can add":
              const remaining = item.max_qty - item.reserved_count;
              html += `
                <div
                  class="counter"
                  data-min="0"
                  data-max="${remaining}"
                  data-current="${item.reserved_count}"
                >
                  <button class="decrement">-</button>
                  <div class="number">${item.reserved_count}</div>
                  <button class="increment">+</button>
                </div>
              `;
            }

            html += `</td>`;
            tr.innerHTML = html;
            tbody.appendChild(tr);
          });

          // re-bind your counters now that they’re in the DOM
          updateCounters();
        }

updateCounters();