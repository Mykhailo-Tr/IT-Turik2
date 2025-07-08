  const deleteModal = document.getElementById('confirmDeleteModal');
  deleteModal.addEventListener('show.bs.modal', event => {
    const button = event.relatedTarget;
    const classId = button.getAttribute('data-id');
    const className = button.getAttribute('data-name');

    const form = deleteModal.querySelector('#deleteForm');
    const nameDisplay = deleteModal.querySelector('#deleteClassName');

    const deleteUrl = `/groups/delete-class/${classId}/`;
    form.action = deleteUrl;
    nameDisplay.textContent = className;
  });