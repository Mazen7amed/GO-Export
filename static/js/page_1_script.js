// for messages
function confirmEditMessage(message, inputElement, hiddenInputElement) {
    var confirmResult = confirm("You are about to edit the " + message + "\nAre you sure you want to proceed?");
    if (confirmResult) {
        var editedValue = prompt("Enter the edited " + message + ":", inputElement.textContent);
        if (editedValue !== null) {
            inputElement.textContent = editedValue; // Update the content of the <pre> element
            if (hiddenInputElement) {
                hiddenInputElement.value = editedValue; // Update the hidden input value if it exists
            }
        }
    }
}


// for dollar and euro rate
function confirmEditNumber(message, inputElement, hiddenInputElement) {
    var confirmResult = confirm("You are about to edit the " + message + "\nAre you sure you want to proceed?");
    if (confirmResult) {
        // Remove the 'disabled' attribute if present
        inputElement.removeAttribute("disabled");
        
        var editedValue = prompt("Enter the edited " + message + ":", inputElement.value);
        if (editedValue !== null) {
            inputElement.value = editedValue; // Update the value of the input element
            if (hiddenInputElement) {
                hiddenInputElement.value = editedValue; // Update the hidden input value if it exists
            }
        }
        
        // Re-enable the input field
        inputElement.setAttribute("disabled", "disabled");
    }
}


function editField(fieldId, hiddenFieldId, message) {
    var inputField = document.getElementById(fieldId);
    var hiddenInput = document.getElementById(hiddenFieldId);
    confirmEditMessage(message, inputField, hiddenInput);
}



function editFieldNumber(fieldId, hiddenFieldId, message) {
    var inputField = document.getElementById(fieldId);
    var hiddenInput = document.getElementById(hiddenFieldId);
    confirmEditNumber(message, inputField, hiddenInput);
}

function editDollarRate() {
    editFieldNumber("dollarRate", "Default_dollar_rate", "Dollar Rate");
}

function editEuroRate() {
    editFieldNumber("euroRate", "Default_euro_rate", "Euro Rate");
}

function editGoMessage() {
    editField("goMessage", "defaultGoMessage", "G&O Message");
}

function editMessageToClient() {
    editField("messageToClient", "defaultClientMessage", "Client Message");
}
