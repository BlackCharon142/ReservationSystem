document.addEventListener('DOMContentLoaded', function () {
    const picker = document.querySelector('.date-picker');
    const clearBtn = document.querySelector('.clear-date');

    if (!picker) return;

    function filterMeals() {
        const tsStr = picker.getAttribute('data-timestamp');
        const valid = tsStr && tsStr !== 'null';
        const ts = valid ? parseInt(tsStr, 10) : NaN;

        // show/hide clear button
        clearBtn.style.display = valid ? 'block' : 'none';
        picker.style.paddingRight = valid ? '25px' : '';


        // compute day window only if valid
        let startTs, endTs;
        if (valid && !isNaN(ts)) {
            const d = new Date(ts * 1000);
            const sd = new Date(d.getFullYear(), d.getMonth(), d.getDate());
            startTs = Math.floor(sd.getTime() / 1000);
            endTs = startTs + 24 * 60 * 60;
        }

        document.querySelectorAll('.meal').forEach(meal => {
            const expEl = meal.querySelector('.meal-expiration');
            if (!expEl) return;

            if (!valid) {
                // no filter → show all
                meal.style.display = '';
            } else {
                const expTs = parseInt(expEl.getAttribute('data-timestamp'), 10);
                meal.style.display = (expTs >= startTs && expTs < endTs)
                    ? ''
                    : 'none';
            }
        });
    }

    // watch for standard change (if plugin fires it)
    picker.addEventListener('change', filterMeals);

    // also catch the plugin writing data-timestamp even without a change event
    new MutationObserver(muts => {
        muts.forEach(m => {
            if (m.attributeName === 'data-timestamp') {
                filterMeals();
            }
        });
    }).observe(picker, { attributes: true, attributeFilter: ['data-timestamp'] });

    // clear button
    clearBtn.addEventListener('click', () => {
        picker.removeAttribute('data-timestamp');
        picker.value = '';
        filterMeals();
    });

    // initial run
    filterMeals();
});