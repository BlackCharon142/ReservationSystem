document.addEventListener("DOMContentLoaded", () => {
    const editButtons = document.querySelectorAll(".edit-daily-menu");
    const deleteButtons = document.querySelectorAll(".delete-daily-menu");

    editButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const row = btn.closest(".reservation-log-row");

            // Set hidden ID field
            document.getElementById("daily-menu-id").value = row.dataset.id;

            // Set selects
            document.querySelector("select#food").value = row.dataset.food;
            document.querySelector("select#drink").value = row.dataset.drink;
            document.querySelector("select#meal_type").value = row.dataset.mealType;

            // Set side dish checkboxes
            const selectedSides = JSON.parse(row.dataset.sides.replace(/'/g, '"'));
            document.querySelectorAll(".checkbox-multiselect input[type='checkbox']").forEach(cb => {
                cb.checked = selectedSides.includes(parseInt(cb.value));
            });

            // Quantity, max, price
            document.querySelector("input#quantity").value = row.dataset.quantity;
            document.querySelector("input#max_purchasable_quantity").value = row.dataset.max;
            document.querySelector("input#price").value = row.dataset.price;

            // Reservation Deadline and Expiration
            const rsrvTimestamp = row.dataset.reservationDeadline;
            const expTimestamp = row.dataset.expiration;

            const rsrvInput = document.querySelector("input#reservation_deadline_display");
            const expInput = document.querySelector("input#expiration_date_display");

            if (rsrvInput && rsrvTimestamp) {
                rsrvInput.setAttribute("data-timestamp", rsrvTimestamp);
                rsrvInput.value = row.querySelector("td:nth-child(2)").innerText; // already formatted Jalali
            }

            if (expInput && expTimestamp) {
                expInput.setAttribute("data-timestamp", expTimestamp);
                expInput.value = row.querySelector("td:nth-child(2)").innerText;
            }

            const imgPreview = document.getElementById("current-image");
            imgPreview.src = row.dataset.imageUrl;
            imgPreview.style.display = "block";

            document.querySelector(".add-edit-form").scrollIntoView({ behavior: "smooth" });
        });
    });

    deleteButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const id = btn.dataset.id;
            if (confirm("آیا مطمئن هستید که می‌خواهید این مورد را حذف کنید؟")) {
                fetch(`/admin/daily-menu-items/delete/${id}/`, {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": getCSRFToken(),
                    },
                }).then(res => {
                    if (res.ok) {
                        const row = btn.closest('tr');
                        row.remove();

                        const currentFormId = document.getElementById('daily-menu-id').value;
                        if (currentFormId === id) {
                            document.getElementById('daily-menu-form').reset();
                            document.getElementById('daily-menu-id').value = '';
                        }
                    } else {
                        alert("خطایی در حذف آیتم رخ داد");
                    }
                });
            }
        });
    });

    document.querySelector(".add-edit-form").addEventListener("submit", function (e) {
        const reservationDisplay = document.getElementById("reservation_deadline_display");
        const reservationHidden = document.getElementById("reservation_deadline");

        const expirationDisplay = document.getElementById("expiration_date_display");
        const expirationHidden = document.getElementById("expiration_date");

        reservationHidden.value = reservationDisplay.dataset.timestamp || "";
        expirationHidden.value = expirationDisplay.dataset.timestamp || "";
    });

    function getCSRFToken() {
        const csrf = document.querySelector("[name=csrfmiddlewaretoken]");
        return csrf ? csrf.value : "";
    }

    document.getElementById("image").addEventListener("change", function (event) {
        const file = event.target.files[0];
        const preview = document.getElementById("current-image");

        if (file) {
            const reader = new FileReader();
            reader.onload = function (e) {
                preview.src = e.target.result;
                preview.style.display = "inline-block";
            };
            reader.readAsDataURL(file);
        } else {
            preview.src = "";
            preview.style.display = "none";
        }
    });
});