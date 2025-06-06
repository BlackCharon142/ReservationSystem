document.addEventListener('DOMContentLoaded', () => {
    // Edit user
    document.querySelectorAll('.edit-user').forEach(btn => {
        btn.addEventListener('click', () => {
            const id = btn.dataset.id;
            const row = btn.closest('tr');

            document.getElementById('user-id').value = id;
            document.getElementById('user-username').value = row.dataset.username || '';
            document.getElementById('user-firstname').value = row.querySelector('.user-firstname')?.textContent.trim() || '';
            document.getElementById('user-lastname').value = row.querySelector('.user-lastname')?.textContent.trim() || '';
            document.getElementById('user-email').value = row.dataset.email || '';
            document.getElementById('user-phone').value = row.dataset.phone || '';
            document.getElementById('user-wallet').value = row.dataset.wallet || '';

            // Security answers
            document.querySelector('[name="security_answer_1"]').value = row.dataset.securityAnswer1 || '';
            document.querySelector('[name="security_answer_2"]').value = row.dataset.securityAnswer2 || '';
            document.querySelector('[name="security_answer_3"]').value = row.dataset.securityAnswer3 || '';
            document.querySelector('[name="security_answer_4"]').value = row.dataset.securityAnswer4 || '';
            document.querySelector('[name="security_answer_5"]').value = row.dataset.securityAnswer5 || '';

            // Allowed meals
            ['صبحانه', 'نهار', 'شام', 'میان وعده'].forEach(mealTitle => {
                document.querySelectorAll('#user-form .allowed-meals-container input[type="checkbox"]').forEach(cb => {
                    const label = cb.nextElementSibling?.textContent.trim();
                    cb.checked = row.querySelector('.user-meals')?.textContent.includes(label);
                });
            });
            // Admin checkbox
            document.getElementById('user-is-admin').checked = row.dataset.admin === 'True';

            const imgPreview = document.getElementById("current-profile-image");
            imgPreview.src = row.dataset.imageUrl;
            imgPreview.style.display = "block";
        });
    });


    // Delete user
    document.querySelectorAll('.delete-user').forEach(btn => {
        btn.addEventListener('click', () => {
            if (confirm('آیا از حذف کاربر اطمینان دارید؟')) {
                const id = btn.dataset.id;

                fetch(`/admin/users/delete/${id}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                    },
                })
                    .then(res => {
                        if (res.ok) {
                            const row = btn.closest('tr');
                            row.remove();

                            const currentFormId = document.getElementById('user-id').value;
                            if (currentFormId === id) {
                                document.getElementById('user-form').reset();
                                document.getElementById('user-id').value = '';
                            }
                        } else {
                            alert('خطا در حذف کاربر');
                        }
                    });
            }
        });
    });

        document.getElementById("profile-image").addEventListener("change", function (event) {
        const file = event.target.files[0];
        const preview = document.getElementById("current-profile-image");

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
