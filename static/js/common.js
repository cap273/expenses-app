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

function isValidDate(day, monthName, year) {
    var monthIndex = new Date(Date.parse(monthName +" 1, 2020")).getMonth(); // Get month as a number
    var parsedDate = new Date(year, monthIndex, day);

    // Check if the parsed date's year, month, and day match the input values
    return parsedDate.getFullYear() == year &&
           parsedDate.getMonth() == monthIndex &&
           parsedDate.getDate() == day;
}