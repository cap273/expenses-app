document.getElementById('addRowBtn').addEventListener('click', function() {
    var table = document.getElementById('inputTable');
    var newRow = table.insertRow(-1);

    var cell1 = newRow.insertCell(0);
    var cell2 = newRow.insertCell(1);
    var cell3 = newRow.insertCell(2);
    var cell4 = newRow.insertCell(3);
    var cell5 = newRow.insertCell(4);
    var cell6 = newRow.insertCell(5);

    cell1.innerHTML = '<input type="text" name="day[]">';
    cell2.innerHTML = '<input type="text" name="month[]">';
    cell3.innerHTML = '<input type="text" name="year[]">';
    cell4.innerHTML = '<input type="text" name="amount[]">';
    cell5.innerHTML = '<input type="text" name="category[]">';
    cell6.innerHTML = '<input type="text" name="notes[]">';
});

document.getElementById('deleteRowBtn').addEventListener('click', function() {
    var table = document.getElementById('inputTable');
    var rowCount = table.rows.length;
    if (rowCount > 2) { // Keeps the header and first row
        table.deleteRow(rowCount - 1);
    }
});