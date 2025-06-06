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

                    // Remove guest from <select>
                    const guestSelect = document.getElementById('guest-select');
                    const optionToRemove = guestSelect.querySelector(`option[value="${id}"]`);
                    if (optionToRemove) {
                        optionToRemove.remove();
                    }

                    window.location.reload();
                } else {
                    alert('خطا در حذف');
                }
            });
        }
    });
});

document.querySelectorAll(".edit-reservation").forEach(function (editBtn) {
    editBtn.addEventListener("click", function () {
        const row = this.closest("tr");

        // Fill form fields from row dataset
        document.getElementById("guest-select").value = row.dataset.guestId;
        document.getElementById("meal-select").value = row.dataset.menuId;
        document.getElementById("reservation-id").value = row.dataset.id;
    });
});

document.querySelectorAll(".cancel-reservation").forEach(function (btn) {
  btn.addEventListener("click", function () {
    const id = this.dataset.id;
    if (!confirm("آیا از لغو رزرو مطمئن هستید؟")) return;

    fetch("/admin/guests/cancel-reservation/", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-CSRFToken": document.querySelector("input[name=csrfmiddlewaretoken]").value
      },
      body: `id=${encodeURIComponent(id)}`
    })
    .then(response => {
      if (!response.ok) throw new Error("Failed to cancel reservation");
      return response.json();
    })
    .then(data => {
      alert("رزرو با موفقیت لغو شد.");
      location.reload();
    })
    .catch(error => {
      alert("خطا در لغو رزرو.");
      console.error(error);
    });
  });
});