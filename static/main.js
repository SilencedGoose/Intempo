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
