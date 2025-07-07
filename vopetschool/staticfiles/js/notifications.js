// === notifications.js ===
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
    let notifications = [];

    function renderNotifications() {
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
                notifications = notifications.filter(item => item.id !== n.id);
                renderNotifications();

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
            notifications = [];
            renderNotifications();
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

        renderNotifications();
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

    // === WebSocket setup ===
    const wsScheme = window.location.protocol === "https:" ? "wss" : "ws";
    const socket = new WebSocket(`${wsScheme}://${window.location.host}/ws/notifications/`);

    socket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        if (data.notifications) {
            notifications = data.notifications;
            renderNotifications();
        }
    };

    socket.onclose = function() {
        console.warn("WebSocket connection closed.");
    };

    socket.onerror = function(err) {
        console.error("WebSocket error:", err);
    };
});