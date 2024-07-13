function confirmEdit(message, inputElement, hiddenInputElement) {
    var confirmResult = confirm("You are about to edit the " + message + "\nAre you sure you want to proceed?");
    if (confirmResult) {
        var editedValue = prompt("Enter the edited " + message + ":", inputElement.value);
        if (editedValue !== null) {
            inputElement.value = editedValue; // Update value instead of textContent
            hiddenInputElement.value = editedValue;
        }
    }
}


function editweekNo() {
    var weekNoInput = document.getElementById("weekNo");
    var hiddenInput = document.getElementById("defaultweekNo");
    confirmEdit("Number of Weeks", weekNoInput, hiddenInput);
}


function editGoFees() {
    var goFeesInput = document.getElementById("go_fees");
    var hiddenInput = document.getElementById("defaultgo_fees");
    confirmEdit("G&O Fees %", goFeesInput, hiddenInput);
}

function editShipping() {
    var shippingInput = document.getElementById("germanyShipping");
    var hiddenInput = document.getElementById("defaultShipping");
    confirmEdit("Germany Shipping", shippingInput, hiddenInput);
}

function editcustom_Fees() {
    var customFeesInput = document.getElementById("custom_Fees");
    var hiddenInput = document.getElementById("defaultcustom_Fees");
    confirmEdit("Port Custom Fees", customFeesInput, hiddenInput);
}

function editDestCity() {
    var DestCityInput = document.getElementById("destination_city");
    var hiddenInput = document.getElementById("defaultDestCity");
    confirmEdit("Destination City", DestCityInput, hiddenInput);
}


// Get the checkbox and warning message elements
var checkbox = document.getElementById("manualCheckbox");
var warningMessage = document.getElementById("warningMessage");

if (checkbox && warningMessage) {
    // Add event listener to the checkbox
    checkbox.addEventListener("change", function () {
        // If checkbox is checked, display the warning message, otherwise hide it
        if (checkbox.checked) {
            warningMessage.style.display = "block";
        } else {
            warningMessage.style.display = "none";
        }
    });
} else {
    console.error("Checkbox or warning message element not found.");
}


// Update the checkbox state and hidden input value when it changes
function updateCheckboxState() {
    var checkbox = document.getElementById("manualCheckbox");
    var hiddenInput = document.getElementById("hidden_manualCheckbox");
    if (checkbox && hiddenInput) {
        hiddenInput.value = checkbox.checked ? "true" : "false";
    }
}

// Add event listener to the checkbox to update its state
var checkbox = document.getElementById("manualCheckbox");
if (checkbox) {
    checkbox.addEventListener("change", updateCheckboxState);
}

// Initialize the checkbox state
updateCheckboxState();





 function editCheckboxChange() {
            var checkbox = document.getElementById("editCheckbox");
            var inputContainers = document.querySelectorAll(".input-container");

            if (checkbox.checked) {
                // Show input containers
                inputContainers.forEach(function(container) {
                    container.classList.remove('hidden');
                });
            } else {
                // Hide input containers
                inputContainers.forEach(function(container) {
                    container.classList.add('hidden');
                });
            }
        }

function updateCheckboxState() {
    var checkbox = document.getElementById("editCheckbox");
    var hiddenInput = document.getElementById("hidden_editCheckbox");

    if (checkbox && hiddenInput) {
        hiddenInput.value = checkbox.checked ? "true" : "false";
        editCheckboxChange(); // Call this function to initially set visibility
    }
}

// Initialize checkbox state
updateCheckboxState();