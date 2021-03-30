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
                    $("#number-of-reviews").text("1 Review");
                } else {
                    $("#number-of-reviews").text(`${response["no_of_reviews"]} Reviews`);
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
    
                console.log("Successfully add the review!", true);
            },
            error: function (request) {
                console.log(request["error"])
            }
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

                console.log("Successfully added comment!");
            },
            error: function (request) {
                console.log(request["error"])
            }
        });
    });
})
