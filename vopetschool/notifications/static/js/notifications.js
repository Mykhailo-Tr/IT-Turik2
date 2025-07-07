document.addEventListener("DOMContentLoaded", () => {
    const alerts = document.querySelectorAll('#messages-container .alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            bootstrap.Alert.getOrCreateInstance(alert).close();
        }, 2500);
    });

    const bell = document.getElementById("notificationBell");
    const dropdownMenu = document.getElementById("notificationDropdownMenu");
    const badge = document.getElementById("notification-count");

    let isDropdownVisible = false;

    async function fetchNotifications() {
        try {
            const res = await fetch("/notifications/api/");
            const data = await res.json();
            return data.notifications || [];
        } catch {
            return [];
        }
    }

    async function renderNotifications() {
        const notifications = await fetchNotifications();
        dropdownMenu.innerHTML = "";

        if (notifications.length === 0) {
            dropdownMenu.innerHTML = `<li><span class="dropdown-item text-muted">Немає нових сповіщень</span></li>`;
            badge.style.display = "none";
            return;
        }

        badge.textContent = notifications.length;
        badge.style.display = "inline-block";

        notifications.forEach(n => {
            const li = document.createElement("li");
            li.classList.add("notification-item");

            const a = document.createElement("a");
            a.className = "dropdown-item";
            a.href = n.link || "#";
            a.textContent = n.message;

            a.addEventListener("click", async e => {
                e.stopPropagation();

                await fetch("/notifications/delete-single/", {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": getCookie("csrftoken"),
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({ id: n.id })
                });

                li.remove();
                const remaining = dropdownMenu.querySelectorAll("li.notification-item").length;
                if (remaining === 0) {
                    dropdownMenu.innerHTML = `<li><span class="dropdown-item text-muted">Немає нових сповіщень</span></li>`;
                    badge.style.display = "none";
                } else {
                    badge.textContent = remaining;
                }

                window.location.href = n.link;
            });

            li.appendChild(a);
            dropdownMenu.appendChild(li);
        });

        const divider = document.createElement("li");
        divider.innerHTML = `<hr class="dropdown-divider">`;
        dropdownMenu.appendChild(divider);

        const clearBtn = document.createElement("button");
        clearBtn.className = "dropdown-item text-danger fw-semibold";
        clearBtn.textContent = "🗑️ Очистити всі";

        clearBtn.addEventListener("click", async () => {
            await fetch("/notifications/delete/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCookie("csrftoken"),
                    "Content-Type": "application/json",
                }
            });
            dropdownMenu.innerHTML = `<li><span class="dropdown-item text-muted">Немає нових сповіщень</span></li>`;
            badge.style.display = "none";
        });

        const clearItem = document.createElement("li");
        clearItem.appendChild(clearBtn);
        dropdownMenu.appendChild(clearItem);
    }

    bell?.addEventListener("click", async e => {
        e.stopPropagation();

        if (isDropdownVisible) {
            dropdownMenu.style.display = "none";
            isDropdownVisible = false;
            document.removeEventListener("click", outsideClickHandler);
            return;
        }

        await renderNotifications();
        dropdownMenu.style.display = "block";
        isDropdownVisible = true;
        document.addEventListener("click", outsideClickHandler);
    });

    function outsideClickHandler(event) {
        if (!dropdownMenu.contains(event.target) && !bell.contains(event.target)) {
            dropdownMenu.style.display = "none";
            isDropdownVisible = false;
            document.removeEventListener("click", outsideClickHandler);
        }
    }

    function getCookie(name) {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                return decodeURIComponent(cookie.substring(name.length + 1));
            }
        }
        return null;
    }

    async function updateBadge() {
        const notifications = await fetchNotifications();
        if (notifications.length > 0) {
            badge.textContent = notifications.length;
            badge.style.display = "inline-block";
        } else {
            badge.style.display = "none";
        }
    }

    updateBadge();
    setInterval(updateBadge, 5000);
});
