// Fill form on edit
document.querySelectorAll(".edit-guest").forEach(function (btn) {
    btn.addEventListener("click", function () {
        const row = btn.closest("tr");

        document.getElementById("guest-id").value = row.dataset.id;
        document.getElementById("guest-first-name").value = row.dataset.firstName;
        document.getElementById("guest-last-name").value = row.dataset.lastName;
        document.getElementById("guest-email").value = row.dataset.email;
        document.getElementById("guest-phone").value = row.dataset.phone;
    });
});

// Confirm delete
document.querySelectorAll(".delete-guest").forEach(function (btn) {
    btn.addEventListener("click", function () {
        const row = btn.closest("tr");
        const id = row.dataset.id;
        if (confirm("آیا مطمئن هستید؟")) {
            fetch(`/admin/guests/delete/${id}/`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": "{{ csrf_token }}",
                }
            }).then(res => {
                if (res.ok) {
                    row.remove();

                    // Clear form if this was the selected sidedish
                    if (document.getElementById('guest-id').value === id) {
                        document.getElementById('guest-id').value = '';
                        document.getElementById('guest-first-name').value = '';
                        document.getElementById('guest-last-name').value = '';
                        document.getElementById('guest-email').value = '';
                        document.getElementById('guest-phone').value = '';
                    }
                } else {
                    alert('خطا در حذف');
                }
            });
        }
    });
});