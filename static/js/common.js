document.addEventListener('DOMContentLoaded', function() {
    var displayNameElement = document.getElementById('display_name');
    var dropdownMenu = document.getElementById('dropdownMenu');

    if (displayNameElement && dropdownMenu) {
        displayNameElement.addEventListener('click', function(event) {
            // Prevents the click event from affecting parent elements
            event.stopPropagation();
            // Toggles the display of the dropdown
            dropdownMenu.style.display = dropdownMenu.style.display === 'block' ? 'none' : 'block';
        });

        // Close the dropdown if clicked outside
        window.onclick = function(event) {
            if (!event.target.matches('.display_name') && dropdownMenu.style.display === 'block') {
                dropdownMenu.style.display = 'none';
            }
        }
    } else {
        console.log('Display name element or dropdown menu not found.');
    }
});