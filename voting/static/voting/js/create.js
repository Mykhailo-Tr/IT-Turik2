document.addEventListener("DOMContentLoaded", function () {
    const container = document.getElementById("formset-container");
    const addBtn = document.getElementById("add-option");
    const totalForms = document.getElementById("id_form-TOTAL_FORMS");

    function updateFormIndexes() {
        const forms = container.querySelectorAll(".formset-form");
        forms.forEach((form, index) => {
            form.querySelectorAll("input, label").forEach(el => {
                if (el.name) el.name = el.name.replace(/form-\d+-/, `form-${index}-`);
                if (el.id) el.id = el.id.replace(/form-\d+-/, `form-${index}-`);
                if (el.htmlFor) el.htmlFor = el.htmlFor.replace(/form-\d+-/, `form-${index}-`);
            });
        });
        totalForms.value = forms.length;
    }

    function attachRemoveHandlers() {
        const removeButtons = container.querySelectorAll(".remove-option");
        removeButtons.forEach(button => {
            button.onclick = function () {
                const forms = container.querySelectorAll(".formset-form");
                if (forms.length > 2) {
                    this.closest(".formset-form").remove();
                    updateFormIndexes();
                } else {
                    alert("Має бути щонайменше 2 варіанти.");
                }
            };
        });
    }

    addBtn.addEventListener("click", function () {
        const total = parseInt(totalForms.value);
        const newForm = container.querySelector(".formset-form").cloneNode(true);

        newForm.querySelectorAll("input").forEach(input => {
            if (input.type === "checkbox") input.checked = false;
            else input.value = "";
        });

        newForm.querySelectorAll("input, label").forEach(el => {
            if (el.name) el.name = el.name.replace(/form-(\d+)-/, `form-${total}-`);
            if (el.id) el.id = el.id.replace(/form-(\d+)-/, `form-${total}-`);
            if (el.htmlFor) el.htmlFor = el.htmlFor.replace(/form-(\d+)-/, `form-${total}-`);
        });

        container.appendChild(newForm);
        totalForms.value = total + 1;
        attachRemoveHandlers();
    });

    attachRemoveHandlers();

    const levelField = document.getElementById("id_level");
    const participantsField = document.querySelector(".field-participants");
    const teacherGroupsField = document.querySelector(".field-teacher_groups");
    const classGroupsField = document.querySelector(".field-class_groups");

    function toggleFields() {
        const level = levelField.value;
        if (participantsField) participantsField.style.display = (level === "selected") ? "block" : "none";
        if (teacherGroupsField) teacherGroupsField.style.display = (level === "teachers") ? "block" : "none";
        if (classGroupsField) classGroupsField.style.display = (level === "class") ? "block" : "none";
    }

    if (levelField) {
        levelField.addEventListener("change", toggleFields);
        toggleFields();
    }
});