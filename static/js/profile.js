function addPerson() {
    const container = document.getElementById('person-container');
    const newPersonDiv = document.createElement('div');
    newPersonDiv.className = 'person-entry';
    newPersonDiv.innerHTML = `
        <span>New.</span>
        <input type="hidden" name="person_ids[]" value="new">
        <input type="text" name="person_names[]">
        <button type="button" class="inform-profile-btn" onclick="removePerson(this)">Remove</button>`;
    container.appendChild(newPersonDiv);
}

function removePerson(element) {
    element.parentElement.remove();
}