//will display a warning message if user tries to leave page while filling out a form
//can be used to tell user that comment will not be saved if they try to leave page before submitting

var formSubmitting = false;
var setFormSubmitting = function() {
	formSubmitting = true;
}

window.onload = function() {
    window.addEventListener("beforeunload", function (e) {
        if (formSubmitting) {
            (e || window.event).returnValue = '';
            return undefined;
        }

    });
};

//// profile view
// showing/hiding the forms to edit profile
function toggle_edit_profile() {
	var e = document.getElementById("user_form");

	if (e.style.display == "none") {
		e.style.display = "block";
	} else {
		e.style.display = "none";
	}
}
