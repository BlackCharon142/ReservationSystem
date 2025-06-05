document.addEventListener("DOMContentLoaded", () => {
    // Edit
    document.querySelectorAll(".edit-food").forEach(btn => {
        btn.addEventListener("click", () => {
            const row = btn.closest("tr");
            document.getElementById("food-id").value = row.dataset.id;
            document.getElementById("food-name").value = row.dataset.name;
            document.getElementById("food-description").value = row.dataset.description;

            const imgPreview = document.getElementById("current-image");
            imgPreview.src = row.dataset.imageUrl;
            imgPreview.style.display = "block";
        });
    });

    // Delete
    document.querySelectorAll(".delete-food").forEach(btn => {
        btn.addEventListener("click", () => {
            const row = btn.closest("tr");
            const id = row.dataset.id;
            if (confirm("آیا مطمئن هستید؟")) {
                fetch(`/admin/foods/delete/${id}/`, {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": "{{ csrf_token }}",
                    }
                }).then(res => {
                    if (res.ok) {
                        row.remove();

                        // Clear form if this was the selected sidedish
                        if (document.getElementById('food-id').value === id) {
                            document.getElementById('food-id').value = '';
                            document.getElementById('food-name').value = '';
                            document.getElementById('food-description').value = '';

                            const imgPreview = document.getElementById("current-image");
                            imgPreview.src = "";
                            imgPreview.style.display = "none";
                        }
                    } else {
                        alert('خطا در حذف');
                    }
                });
            }
        });
    });

    document.getElementById("food-image").addEventListener("change", function (event) {
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
