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

// keeps track of the value that the user has selected when sliding the range
function onRatingChange(form) {
    $("#rating-value").html($(form).val())
}