document.addEventListener('DOMContentLoaded', () => {
  // Edit drink
  document.querySelectorAll('.edit-drink').forEach(btn => {
    btn.addEventListener('click', () => {
      document.getElementById('drink-id').value = btn.dataset.id;
      document.getElementById('drink-name').value = btn.dataset.name;
      document.getElementById('drink-description').value = btn.dataset.description;
    });
  });

  // Delete drink
  document.querySelectorAll('.delete-drink').forEach(btn => {
    btn.addEventListener('click', () => {
      if (confirm('آیا از حذف اطمینان دارید؟')) {
        const id = btn.dataset.id;

        fetch(`/admin/drinks/delete/${id}/`, {
          method: 'POST',
          headers: {
            'X-CSRFToken': '{{ csrf_token }}',
          },
        })
        .then(res => {
          if (res.ok) {
            // Remove the row
            const row = btn.closest('tr');
            row.remove();

            // Clear form if deleted item was being edited
            const currentFormId = document.getElementById('drink-id').value;
            if (currentFormId === id) {
              document.getElementById('drink-id').value = '';
              document.getElementById('drink-name').value = '';
              document.getElementById('drink-description').value = '';
            }
          } else {
            alert('خطا در حذف آیتم');
          }
        });
      }
    });
  });
});
