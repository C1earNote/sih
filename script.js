
const sidebar = document.querySelector('.side-bar');
const taskbarImg = document.querySelector('.taskbar img');

taskbarImg.addEventListener('mouseenter', () => {
    sidebar.classList.add('active');
});

sidebar.addEventListener('mouseleave', () => {
    sidebar.classList.remove('active');
});
