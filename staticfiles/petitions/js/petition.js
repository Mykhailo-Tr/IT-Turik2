document.addEventListener("DOMContentLoaded", function () {
    const formWrapper = document.getElementById("support-button-wrapper");
    const countElem = document.getElementById("support-count");
    const progressElem = document.getElementById("support-progress");
    const requiredElem = document.getElementById("required-supporters");
    const remainingElem = document.getElementById("remaining-supporters");

    // 🔁 Оновлення кількості підтримки
    function refreshSupportData() {
        const supportUrl = formWrapper?.dataset.supportUrl;
        if (!supportUrl) return;

        fetch(supportUrl + "?refresh=1")
            .then(r => r.json())
            .then(data => {
                // 🔢 Лічильник підтримки
                countElem.textContent = data.supporters_count;

                // 📊 Прогресбар
                progressElem.style.width = data.support_percent + "%";
                progressElem.setAttribute("aria-valuenow", data.support_percent);
                progressElem.textContent = data.support_percent + "%";

                // 📈 Додаткові лічильники
                if (requiredElem) requiredElem.textContent = data.required_supporters;
                if (remainingElem) remainingElem.textContent = data.remaining_supporters;
            });
    }

    // 🕓 Автоматичне оновлення кожні 2 секунди
    setInterval(refreshSupportData, 2000);

    // ⚡ Обробка натискання кнопки підтримки
    if (formWrapper) {
        formWrapper.addEventListener("submit", function (e) {
            e.preventDefault();

            const form = e.target;
            const formData = new FormData(form);
            const isCancel = formData.get("cancel");

            fetch(form.action, {
                method: "POST",
                headers: {
                    "X-CSRFToken": form.querySelector('[name=csrfmiddlewaretoken]').value,
                },
                body: formData
            }).then(response => response.json())
              .then(data => {
                if (data.success) {
                    // 🔄 Оновлення лічильника і прогресу
                    countElem.textContent = data.supporters_count;
                    progressElem.style.width = data.support_percent + "%";
                    progressElem.setAttribute("aria-valuenow", data.support_percent);
                    progressElem.textContent = data.support_percent + "%";

                    // 🔄 Оновлення додаткових лічильників
                    if (requiredElem) requiredElem.textContent = data.required_supporters;
                    if (remainingElem) remainingElem.textContent = data.remaining_supporters;

                    // 🔁 Динамічне оновлення кнопки
                    const newForm = document.createElement("form");
                    newForm.method = "post";
                    newForm.action = form.action;
                    newForm.id = "support-form";

                    const csrf = document.createElement("input");
                    csrf.type = "hidden";
                    csrf.name = "csrfmiddlewaretoken";
                    csrf.value = form.querySelector('[name=csrfmiddlewaretoken]').value;
                    newForm.appendChild(csrf);

                    if (!isCancel) {
                        const hidden = document.createElement("input");
                        hidden.type = "hidden";
                        hidden.name = "cancel";
                        hidden.value = "1";
                        newForm.appendChild(hidden);
                    }

                    const btn = document.createElement("button");
                    btn.type = "submit";
                    btn.className = "btn rounded-pill " + (isCancel ? "btn-outline-primary" : "btn-outline-danger");
                    btn.innerHTML = isCancel ? "🙋 Підтримати петицію" : "❌ Скасувати підтримку";

                    newForm.appendChild(btn);

                    formWrapper.innerHTML = "";
                    formWrapper.appendChild(newForm);
                }
            });
        });
    }
});
