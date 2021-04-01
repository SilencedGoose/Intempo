var review_id;
var album_sort_type = 'avg_rating';

function setReviewId(id) {
    review_id = id;
}

function setAlbumSortType(type) {
    album_sort_type = type;
}

$(function () {
    $("#addCommentModal").on("hidden.bs.modal", function () {
        $("#add-comment-form").trigger('reset');
    });

    $("#add-review-form").submit(function (e) {
        e.preventDefault();
        var form = $(this).serialize();
    
        $.ajax({
            type: 'POST',
            url: `./add_review/`,
            data: form,
            success: function (response) {
                // updated average review value
                $("#album-rating").text(response["avg_rating"].toFixed(1));
    
                // update the number of reviews
                if (response["no_of_reviews"] == 1) { 
                    $("#number-of-reviews").text("1 Review With Comment");
                } else {
                    $("#number-of-reviews").text(`${response["no_of_reviews"]} Reviews With Comment`);
                }
    
                // close addReviewModal
                $('#addReviewModal').modal('hide');
    
                // remove add review button and modal
                $("#add-review").remove();
                $("#addReviewModal").remove();
    
                if (response["review_text"].length > 0) {
                    // add the comments modal at the end of the modals
                    var commentsModalDiv = `
                    <div class="modal fade comments-modal" tabindex="-1" id="comments${response["review_id"]}Modal" aria-labelledby="comments${response["review_id"]}ModalLabel" aria-hidden="true">
                        <div class="modal-dialog modal-dialog-scrollable">
                            <div class="modal-content">
                                <div class="modal-header">
                                    <h5 class="modal-title">Comments to the review by ${response["username"]}</h5>
                                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                                </div>
                                <div class="modal-body">
                                    <div class="comments">
                                    </div>
                                    <div class="modal-footer">
                                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>`;
                    $("#modals").append(commentsModalDiv);
                    
                    // add the review div at the start of the reviews
                    var reviewDiv = `
                    <div class="card" id="review-${response["review_id"]}">
                        <div class="card-body">
                            <div class="row">
                                <div class="col">
                                    <h5><a href="/intempo/user/${response["username"]}" class="card-title">${response["username"]}</a></h5>
                                    <h6 class="card-subtitle mb-2 text-muted">Just now</h6>
                                </div>
                                <div class="col-auto">
                                    <h4><span class="rating rounded-circle border border-secondary float-end" id="album-rating">${response["user_rating"].toFixed(1)}</span></h4>
                                </div>
                            </div>
                            <div onclick="setReviewId(${response["review_id"]})">
                                <p class="card-text">${response["review_text"]}</p>
                                <a data-bs-toggle="modal" data-bs-target="#comments${response["review_id"]}Modal" 
                                    class="card-link triggers-modal no-comment comments-count">0 Comments</a>
                                <a data-bs-toggle="modal" data-bs-target="#addCommentModal" class="card-link triggers-modal">Add a Comment</a>
                            </div>
                        </div>
                    </div>`;
                    $("#reviews").prepend(reviewDiv);
                }
            },
            error: onAJAXError
        });
    });
    
    $("#add-comment-form").submit(function (e) {
       e.preventDefault();
       var form = $(this).serialize();
    
        $.ajax({
            type: 'POST',
            url: `../${review_id}/add_comment/`,
            data: form,
            success: function (response) {
                // there will be at least 1 comment in this case
                $("#review-" + review_id + " .comments-count").removeClass("no-comment");

                // update the number of comments
                if (response["no_of_comments"] == 1) {
                    $("#review-" + review_id + " .comments-count").text("1 Comment");
                } else {
                    $("#review-" + review_id + " .comments-count").text(`${response["no_of_comments"]} Comments`);
                }
    
                // close the modal (also resets it)
                $("#addCommentModal").modal('hide');
                
                // add the comment to the top of comments
                var commentDiv = `
                <div class="card">
                    <div class="card-body">
                        <h5><a href="/intempo/user/${response["username"]}" class="card-title">${response["username"]}</a></h5>
                        <h6 class="card-subtitle mb-2 text-muted">Just now</h6>
                        <p class="card-text">${response["comment_text"]}</p>
                    </div>
                </div>`;
                $("#comments" + review_id + "Modal .comments").prepend(commentDiv);
            },
            error: onAJAXError
        });
    });

    $("#add-album-form").submit(function (e) {
        e.preventDefault();
        var form = new FormData($(this)[0]);

        var node = $(this);
        // to the form add the img url

        $.ajax({
            type: 'POST',
            url: `./add_album/`,
            data: form,
            cache: false,
            processData: false,
            contentType: false,
            success: function (response) {
                // sorting goes to default- average rating
                $(".set-album-sorting").removeClass("active");
                $("#avg_rating_btn").addClass("active");

                // stop any filtering
                $("#filter-by-tags-form").trigger('reset');
            
                // close the modal
                $("#addAlbumModal").modal('hide');
                // reset the form
                node.trigger('reset');

                updateAlbums(response);
            },
            error: onAJAXError
        });
    });

    $(".set-album-sorting").click(function (e) {
        e.preventDefault();
        var form = $("#filter-by-tags-form").serialize();
        btn = $(this);

        $.ajax({
            type: 'POST',
            url: `./filter_by/${album_sort_type}/`,
            data: form,
            success: function (response) {
                // change which type of sorting we have => make only this type of sorting active
                $(".set-album-sorting").removeClass("active");
                btn.addClass("active");
                updateAlbums(response)
            },
            error: onAJAXError
        });
    });

    $("#filter-by-tags-form").submit(function (e) {
        e.preventDefault();
        var form = $(this).serialize();
        
        $.ajax({
            type: 'POST',
            url: `./filter_by/${album_sort_type}/`,
            data: form,
            success: function (response) {
                var form = new FormData($("#filter-by-tags-form")[0]);
                // if both the fields are empty, to clear button addClass disabled
                if (form.get("fltr") === "" && form.get("search") === "") {
                    $("#clear-button").addClass("disabled");
                } else {
                    $("#clear-button").removeClass("disabled");
                }
                updateAlbums(response);
            },
            error: onAJAXError
        });  
    });

    $("#clear-button").click(function (e) {
        e.preventDefault();
        
        // clear and submit the form
        $("#filter-by-tags-form").trigger('reset');
        $("#filter-by-tags-form").submit();
    })

    $("#update-profile-picture").submit(function (e) {
        e.preventDefault();
        var form = new FormData($(this)[0]);
        var formDiv = $(this);
        
        $.ajax({
            type: 'POST',
            url: `./update_profile/`,
            data: form,
            cache: false,
            processData: false,
            contentType: false,
            success: function (response) {
                // close the modal
                $("#updateProfileModal").modal('hide');

                // reset the form 
                formDiv.trigger('reset');
                // update the profile picture
                $("#profile-picture").attr('src', "/media/" + response["profile_picture"]);
                
                // change the current album link/innerHTML in the form
                $("#div_id_profile_picture a").attr('href', "/media/" + response["profile_picture"]);
                $("#div_id_profile_picture a").text(response["profile_picture"]);
            },
            error: onAJAXError
        });
    });
});

function onAJAXError(response) {
    if (response["responseJSON"]) {
        error = response["responseJSON"]["error"];
        if (error instanceof String) {
            alert(error);
        } else {
            var errors = []
            error = JSON.parse(error);
            for (field in error) {
                error[field].forEach(obj => {
                    errors.push(obj.message);
                })
            }
            if (errors.length == 1) {
                alert("Error: " + errors[0]);
            } else {
                alert("Errors: ", errors.join(", "));
            }
        }
    } else {
        alert("Unexpected error! Please try again!");
    }   
}

function updateAlbums(response) {
    // update the value of tags
    $("#hint_id_fltr").text("Separate the tags by a comma. Available Tags: " + response["tags"].join(", "))

    var no_of_albums = response["albums"].length;
    // update the number of albums
    if (no_of_albums == 1) {
        $("#number-of-albums").text("1 Album");
    } else {
        $("#number-of-albums").text(`${no_of_albums} Albums`);
    }

    // replace the albums
    var albumsDiv = `<div class="row" id="albums">`;
    response["albums"].forEach(album =>{
        albumsDiv += `
        <div class="col-12 col-sm-6 col-md-4 col-lg-3">
            <a href="${album["url"]}">
                <img src="${album["cover"]}" class="img-thumbnail" alt="${album["name"]}">
            </a>
            <p>
                <a href="${album["url"]}"><strong>${album["name"]}</strong></a><br>
                ${album["time_of_creation"]}
                <span class="rating rounded-circle border border-secondary float-end">${album["avg_rating"].toFixed(1)}</span><br>
                ${album["artist"]}<br>
            </p>
        </div>
        `;
    })
    albumsDiv += `</div>`;
    $("#albums").replaceWith(albumsDiv);
}
