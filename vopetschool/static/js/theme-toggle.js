const themeToggle = document.getElementById("themeToggle");
const themeIcon = document.getElementById("themeIcon");
const wave = document.getElementById("theme-wave");

function applyTheme(theme) {
    if (theme === "dark") {
        document.body.classList.add("dark-mode", "dark-gradient");
        document.body.classList.remove("light-gradient");
        themeIcon?.classList.replace("bi-moon-fill", "bi-sun-fill");
    } else {
        document.body.classList.remove("dark-mode", "dark-gradient");
        document.body.classList.add("light-gradient");
        themeIcon?.classList.replace("bi-sun-fill", "bi-moon-fill");
    }
}

const storedTheme = localStorage.getItem("theme");
if (storedTheme) {
    applyTheme(storedTheme);
} else if (window.matchMedia("(prefers-color-scheme: dark)").matches) {
    applyTheme("dark");
}

themeToggle?.addEventListener("click", (e) => {
    const isDark = document.body.classList.contains("dark-mode");
    const newTheme = isDark ? "light" : "dark";
    localStorage.setItem("theme", newTheme);

    const rect = e.target.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;

    const waveColor = newTheme === "dark" ? "#000" : "#fff";
    wave.style.setProperty("--wave-color", waveColor);
    wave.style.left = `${centerX}px`;
    wave.style.top = `${centerY}px`;
    wave.style.width = `0px`;
    wave.style.height = `0px`;
    wave.style.opacity = 0.4;
    wave.style.transform = "scale(0)";
    wave.style.transition = "none";

    requestAnimationFrame(() => {
        wave.style.transition = "transform 0.7s ease-out, opacity 0.5s ease-out";
        wave.style.width = `2000px`;
        wave.style.height = `2000px`;
        wave.style.marginLeft = `-1000px`;
        wave.style.marginTop = `-1000px`;
        wave.style.transform = "scale(2)";
    });

    setTimeout(() => applyTheme(newTheme), 200);
    setTimeout(() => wave.style.opacity = 0, 700);
});
