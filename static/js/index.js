// Access the currency from the user's current session
let currency = document.body.getAttribute('user-currency');
let currencySymbol = currency === 'USD' ? '$' : '€';

// Access list of persons associated with the current user
let persons_json = JSON.parse(document.body.getAttribute('persons_json') || '[]');

// Get all elements with the class 'amount-input-wrapper'
let elements = document.getElementsByClassName('amount-input-wrapper');

// Loop through all elements and add the currency symbol
for(let i = 0; i < elements.length; i++) {
    elements[i].style.setProperty('--currency-symbol', `"${currencySymbol}"`);
}

var addRowBtn = document.getElementById('addRowBtn');
addRowBtn.addEventListener('click', function() {
    var table = document.getElementById('inputTable');
    var newRow = table.insertRow(-1);
    var lastRow = table.rows[table.rows.length - 2]; // Get the last input row

    var lastScope = lastRow.cells[0].querySelector('select').value; // Capture last scope value
    var lastMonth = lastRow.cells[2].querySelector('select').value;
    var lastYear = lastRow.cells[3].querySelector('input').value;

    // Create a new select element for ExpenseScope
    var scopeSelectHTML = '<select name="scope[]" required>' +
        '<option value="" disabled hidden></option>' +
        '<option value="Joint"' + (lastScope === 'Joint' ? ' selected' : '') + '>Joint</option>';

    // Add options for each person
    persons_json.forEach(function(person) {
        scopeSelectHTML += '<option value="' + person.PersonID + '"' +
            (lastScope === String(person.PersonID) ? ' selected' : '') + '>' +
            person.PersonName + '</option>';
    });

    scopeSelectHTML += '</select>';

    var dayInput = '<input type="number" name="day[]" min="1" max="31" required>';
    var monthSelect = '<select name="month[]">' + 
        '<option value="" selected disabled hidden' + (lastMonth === '' ? ' selected' : '') + '></option>' +
        '<option value="January"' + (lastMonth === 'January' ? ' selected' : '') + '>January</option>' +
        '<option value="February"' + (lastMonth === 'February' ? ' selected' : '') + '>February</option>' +
        '<option value="March"' + (lastMonth === 'March' ? ' selected' : '') + '>March</option>' +
        '<option value="April"' + (lastMonth === 'April' ? ' selected' : '') + '>April</option>' +
        '<option value="May"' + (lastMonth === 'May' ? ' selected' : '') + '>May</option>' +
        '<option value="June"' + (lastMonth === 'June' ? ' selected' : '') + '>June</option>' +
        '<option value="July"' + (lastMonth === 'July' ? ' selected' : '') + '>July</option>' +
        '<option value="August"' + (lastMonth === 'August' ? ' selected' : '') + '>August</option>' +
        '<option value="September"' + (lastMonth === 'September' ? ' selected' : '') + '>September</option>' +
        '<option value="October"' + (lastMonth === 'October' ? ' selected' : '') + '>October</option>' +
        '<option value="November"' + (lastMonth === 'November' ? ' selected' : '') + '>November</option>' +
        '<option value="December"' + (lastMonth === 'December' ? ' selected' : '') + '>December</option>' +
        '</select>';
    var yearInput = '<input type="number" name="year[]" min="2000" max="2050" required value="' + lastYear + '">';
    var amountInput = '<div class="amount-input-wrapper"><input type="text" name="amount[]" title="Please enter a valid amount with up to two decimal places. Example: 1,234.56" required></div>';
    var categorySelect = lastRow.cells[5].innerHTML; // Copy the Category dropdown
    var notesInput = '<input type="text" name="notes[]">';

    newRow.innerHTML = `<td>${scopeSelectHTML}</td><td>${dayInput}</td><td>${monthSelect}</td><td>${yearInput}</td><td>${amountInput}</td><td>${categorySelect}</td><td>${notesInput}</td>`;

    // Set focus to the Add Row button
    addRowBtn.focus();
});

var deleteRowBtn = document.getElementById('deleteRowBtn');
deleteRowBtn.addEventListener('click', function() {
    var table = document.getElementById('inputTable');
    var rowCount = table.rows.length;
    if (rowCount > 2) { // Keeps the header and first row
        table.deleteRow(rowCount - 1);
    }

    // Set focus to the Delete Last Row button
    deleteRowBtn.focus();
});

document.addEventListener('input', function(e) {
    if (e.target.name.startsWith('amount')) {
        // Remove all non-numeric characters except for the dot
        let numericValue = e.target.value.replace(/[^\d.]/g, '');

        // Split the input into whole and decimal parts
        let parts = numericValue.split('.');
        if (parts.length > 1) {
            // Restrict to two decimal places
            parts[1] = parts[1].substring(0, 2);
        }

        // Add commas for the thousand separator
        parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ',');

        // Reconstruct the value and update the input field
        e.target.value = parts.join('.');
    }
});

var form = document.getElementById('expensesForm');
form.addEventListener('submit', function(event) {
    var dayInputs = document.querySelectorAll('input[name="day[]"]');
    var monthInputs = document.querySelectorAll('select[name="month[]"]');
    var yearInputs = document.querySelectorAll('input[name="year[]"]');

    for (var i = 0; i < dayInputs.length; i++) {
        var day = dayInputs[i].value;
        var month = monthInputs[i].value;
        var year = yearInputs[i].value;
        if (!isValidDate(day, month, year)) {
            event.preventDefault();  // Stop form submission
            alert("Invalid date: " + month + " " + day + ", " + year);
            return;  // Exit the function
        }
    }
});

