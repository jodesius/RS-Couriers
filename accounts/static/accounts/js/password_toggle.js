// Wires up every eye-icon button on the page to toggle its paired password
// input between masked (dots) and plain text. Buttons are matched to their
// input via data-target="<input id>".
document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.password-toggle').forEach(function (button) {
        const input = document.getElementById(button.getAttribute('data-target'));
        if (!input) {
            return;
        }

        button.addEventListener('click', function () {
            const isCurrentlyVisible = input.type === 'text';
            input.type = isCurrentlyVisible ? 'password' : 'text';
            button.classList.toggle('is-visible', !isCurrentlyVisible);
            button.setAttribute('aria-label', isCurrentlyVisible ? 'Show password' : 'Hide password');
        });
    });
});
