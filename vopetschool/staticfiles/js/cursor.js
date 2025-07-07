const cursorLight = document.getElementById('cursorLight');
document.addEventListener('mousemove', e => {
    cursorLight.style.top = e.clientY + 'px';
    cursorLight.style.left = e.clientX + 'px';
});
