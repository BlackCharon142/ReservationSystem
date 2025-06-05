document.addEventListener('DOMContentLoaded', () => {
  // Handle Edit
  document.querySelectorAll('.edit-sidedish').forEach(btn => {
    btn.addEventListener('click', () => {
      const row = btn.closest('tr');
      document.getElementById('sidedish-id').value = row.dataset.id;
      document.getElementById('sidedish-name').value = row.dataset.name;
      document.getElementById('sidedish-description').value = row.dataset.description;
    });
  });

  // Handle Delete
  document.querySelectorAll('.delete-sidedish').forEach(btn => {
    btn.addEventListener('click', () => {
      if (confirm('حذف شود؟')) {
        const row = btn.closest('tr');
        const id = row.dataset.id;

        fetch(`/admin/sidedishes/delete/${id}/`, {
          method: 'POST',
          headers: {
            'X-CSRFToken': '{{ csrf_token }}',
          }
        }).then(res => {
          if (res.ok) {
            row.remove();

            // Clear form if this was the selected sidedish
            if (document.getElementById('sidedish-id').value === id) {
              document.getElementById('sidedish-id').value = '';
              document.getElementById('sidedish-name').value = '';
              document.getElementById('sidedish-description').value = '';
            }
          } else {
            alert('خطا در حذف');
          }
        });
      }
    });
  });
});