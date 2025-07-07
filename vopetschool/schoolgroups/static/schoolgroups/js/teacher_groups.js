  var editModal = document.getElementById('editGroupModal');
  editModal.addEventListener('show.bs.modal', function (e) {
    var btn = e.relatedTarget;
    var idx = btn.getAttribute('data-index');
    document.querySelectorAll('.edit-group-form').forEach(div => div.classList.add('d-none'));
    var target = document.getElementById('group-form-' + idx);
    if (target) target.classList.remove('d-none');
  });

  var deleteModal = document.getElementById('confirmDeleteModal');
  deleteModal.addEventListener('show.bs.modal', function (event) {
    const button = event.relatedTarget;
    const groupId = button.getAttribute('data-id');
    const groupName = button.getAttribute('data-name');
    const form = deleteModal.querySelector('#deleteGroupForm');
    const nameDisplay = deleteModal.querySelector('#deleteGroupName');

    const deleteUrl = `/groups/delete-group/${groupId}/`;;
    form.action = deleteUrl;
    nameDisplay.textContent = groupName;
  });