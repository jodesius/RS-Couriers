// Wires up the header's dropdown menus - the left "Menu" button, and (when
// logged in) the right profile menu. Click a toggle to open its menu, click
// outside or press Escape to close, and opening one closes the other.
document.addEventListener('DOMContentLoaded', function () {
    const dropdowns = [
        { toggle: document.getElementById('menuToggle'), menu: document.getElementById('dropdownMenu') },
        { toggle: document.getElementById('profileToggle'), menu: document.getElementById('profileDropdown') },
    ].filter(function (pair) {
        return pair.toggle && pair.menu;
    });

    function close(pair) {
        pair.menu.classList.remove('is-open');
        pair.toggle.setAttribute('aria-expanded', 'false');
    }

    function closeAllExcept(exception) {
        dropdowns.forEach(function (pair) {
            if (pair !== exception) {
                close(pair);
            }
        });
    }

    dropdowns.forEach(function (pair) {
        pair.toggle.addEventListener('click', function (event) {
            event.stopPropagation();
            const isOpen = pair.menu.classList.toggle('is-open');
            pair.toggle.setAttribute('aria-expanded', String(isOpen));
            closeAllExcept(pair);
        });
    });

    document.addEventListener('click', function (event) {
        dropdowns.forEach(function (pair) {
            if (!pair.menu.contains(event.target) && !pair.toggle.contains(event.target)) {
                close(pair);
            }
        });
    });

    document.addEventListener('keydown', function (event) {
        if (event.key === 'Escape') {
            closeAllExcept(null);
        }
    });
});
