// static/js/notifications.js
document.addEventListener("DOMContentLoaded", function () {
    const bell = document.getElementById("notificationBell");
    const dropdownMenu = document.getElementById("notificationDropdownMenu");
    const badge = document.getElementById("notification-count");

    let isDropdownVisible = false;
    let notificationsLoaded = false;

    async function fetchNotifications() {
        try {
            const res = await fetch("/notifications/api/");
            const data = await res.json();
            return data.notifications || [];
        } catch (e) {
            console.error("Error fetching notifications:", e);
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
            const a = document.createElement("a");
            a.classList.add("dropdown-item");
            a.href = n.link || "#";
            a.textContent = n.message;

            a.addEventListener("click", async (e) => {
                e.stopPropagation();

                if (n.link && n.link !== "#") {
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
                }

                window.location.href = n.link;
            });

            li.classList.add("notification-item");
            li.appendChild(a);
            dropdownMenu.appendChild(li);
        });

        // 🔘 Кнопка очистити всі
        const divider = document.createElement("li");
        divider.innerHTML = `<hr class="dropdown-divider">`;
        dropdownMenu.appendChild(divider);

        const clearAllItem = document.createElement("li");
        const clearBtn = document.createElement("button");
        clearBtn.className = "dropdown-item text-danger fw-semibold";
        clearBtn.textContent = "🗑️ Очистити всі";
        clearBtn.style.cursor = "pointer";

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

        clearAllItem.appendChild(clearBtn);
        dropdownMenu.appendChild(clearAllItem);
    }

    async function deleteNotifications() {
        try {
            await fetch("/notifications/delete/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCookie("csrftoken"),
                    "Content-Type": "application/json",
                }
            });
            badge.style.display = "none";
            dropdownMenu.innerHTML = `<li><span class="dropdown-item text-muted">Немає нових сповіщень</span></li>`;
        } catch (e) {
            console.error("Error deleting notifications:", e);
        }
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let cookie of cookies) {
                cookie = cookie.trim();
                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    bell.addEventListener("click", async (e) => {
        e.stopPropagation();

        if (isDropdownVisible) {
            // Закриваємо меню і видаляємо повідомлення
            dropdownMenu.style.display = "none";
            isDropdownVisible = false;
            // await deleteNotifications();
            document.removeEventListener("click", outsideClickHandler);
            return;
        }

        // Відкриваємо меню і підвантажуємо нотифікації
        await renderNotifications();
        dropdownMenu.style.display = "block";
        isDropdownVisible = true;

        // Клік поза меню закриває його і видаляє повідомлення
        document.addEventListener("click", outsideClickHandler);
    });

    function outsideClickHandler(event) {
        if (!dropdownMenu.contains(event.target) && !bell.contains(event.target)) {
            dropdownMenu.style.display = "none";
            isDropdownVisible = false;
            // deleteNotifications();
            document.removeEventListener("click", outsideClickHandler);
        }
    }

    // Початковий показ кількості повідомлень (без відкриття меню)
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

    // Оновлюємо бейдж кожні 5 секунд
    setInterval(updateBadge, 5000);
});
