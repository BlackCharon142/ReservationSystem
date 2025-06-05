document.addEventListener('DOMContentLoaded', () => {
    // Edit drink
    document.querySelectorAll('.edit-request').forEach(btn => {
        btn.addEventListener('click', () => {
            document.getElementById("form-id").value = btn.dataset.id;
            document.getElementById("form-username").value = btn.dataset.username;
            document.getElementById("form-firstname").value = btn.dataset.firstname;
            document.getElementById("form-lastname").value = btn.dataset.lastname;
            document.getElementById("form-email").value = btn.dataset.email;
            document.getElementById("form-phone").value = btn.dataset.phone;
            document.getElementById("form-date").value = btn.dataset.date;

            if (btn.dataset.fulfilled === "true") {
                document.getElementById("fulfilled").checked = true;
            } else {
                document.getElementById("pending").checked = true;
            }
        });
    });

});

  document.querySelector('.add-edit-form').addEventListener('submit', function (e) {
    e.preventDefault(); // Temporarily stop submission

    requestAnimationFrame(() => {
      const id = document.getElementById('form-id').value.trim();
      if (!id) {
        alert("هیچ درخواستی انتخاب نشده است!");
      } else {
        // Manually submit if valid
        e.target.submit();
      }
    });
  });