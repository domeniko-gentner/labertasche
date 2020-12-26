

function labertasche_text_counter()
{
    let txt = document.getElementById('labertasche-text');
    let cntr = document.getElementById('labertasche-counter');
    let maxlen = txt.getAttribute("maxlength");
    let helper = document.getElementById("labertasche-text-helper");
    if (cntr && txt){
        cntr.innerText = txt.value.length + "/" + maxlen;
        if (txt.value.length > 40){
            if (helper.classList.contains('is-danger')){
                helper.classList.remove("is-danger");
                helper.classList.add("is-success");
                txt.classList.add('is-success');
                txt.classList.remove('is-danger');
            }
        }
        if (txt.value.length < 40){
            if (helper.classList.contains('is-success')){
                helper.classList.remove("is-success");
                helper.classList.add("is-danger");
                txt.classList.add('is-danger');
                txt.classList.remove('is-success');
            }
        }
    }
}

function labertasche_validate_mail()
{
    let email = document.getElementById("labertasche-mail");
    let is_valid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value);
    if (is_valid){
        email.classList.remove("is-danger")
        email.classList.add("is-success")
    }
    else{
        email.classList.add("is-danger")
        email.classList.remove("is-success")
    }
}

function labertasche_modal_hide()
{
    let modal = document.getElementById('labertasche-modal');
    if (modal != null){
        if (modal.classList.contains("is-active")){
            modal.classList.remove('is-active');
        }
    }
    window.location.reload(true);
}

function labertasche_comment_not_found()
{
    let modal = document.getElementById('labertasche-modal');
    let modal_text = document.getElementById('labertasche-modal-text');
    modal_text.innerText = "The link you followed was not valid. It either doesn't exist or was already used.";
    modal.classList.add('is-active');
}

function labertasche_comment_deleted()
{
    let modal = document.getElementById('labertasche-modal');
    let modal_text = document.getElementById('labertasche-modal-text');
    modal_text.innerText = "Your comment has been deleted. Thank you for being here.";
    modal.classList.add('is-active');
}

/*
    post-min-length
    post-max-length
    post-invalid-json
    post-duplicate
    post-internal-server-error
    post-success
    post-before-fetch
 */
function labertasche_post_callback(state)
{
    // Elements
    let modal = document.getElementById('labertasche-modal');
    let modal_text = document.getElementById('labertasche-modal-text');
    let button = document.getElementById('labertasche-comment-button');

    if (state === "post-before-fetch"){
        button.classList.add("is-loading");
    }
    if (state === "post-min-length"){
        button.classList.remove("is-loading");
        modal_text.innerText = "Your comment was not entered because it is too short. Please write at least 40 characters."
        modal.classList.add('is-active');
    }
    if (state === "post-success"){
        button.classList.remove("is-loading");
        if (state['sendotp']) {
            modal_text.innerText = "Your comment was entered, but you need to confirm it, before it becomes active. Please check your mail!"
        }
        else{
            modal_text.innerText = "Your comment was successfully entered."
        }
        modal.classList.add('is-active');
    }
    if (state === "post-fetch-exception" || state === "post-internal-server-error"){
        button.classList.remove("is-loading");
        modal_text.innerText = "Your comment was not entered because there was an error, which was recorded and reported automatically.";
        modal.classList.add('is-active');
    }
    if (state === "post-duplicate"){
        button.classList.remove("is-loading");
        modal_text.innerText = "This comment was already made.";
        modal.classList.add('is-active');
    }
    if (state === "post-invalid-email"){
        button.classList.remove("is-loading");
        modal_text.innerText = "The email you have entered appears to be invalid. Please contact me if you think this was in error.";
        modal.classList.add('is-active');
    }
}

function labertasche_reply_callback(state, comment_id)
{
    if (state === "on"){
        let comment_btn = document.getElementById('labertasche-comment-button');
        let parent = comment_btn.parentElement
        let new_btn = document.createElement("button");
        new_btn.classList.add("button");
        new_btn.classList.add("is-danger");
        new_btn.classList.add("is-medium");
        new_btn.classList.add("px-6");
        new_btn.setAttribute("id", "labertasche-cancel-reply");
        new_btn.onclick = function() { labertasche_reply_to(-1, labertasche_reply_callback); }
        new_btn.innerHTML = '<span>Cancel Reply</span>';
        parent.appendChild(new_btn);

        comment_btn.innerHTML = "<span class='is-medium'>Reply to #" + comment_id + "</span>";
    }

    if (state === "off"){
        console.log("off");
        let comment_btn = document.getElementById('labertasche-comment-button');
        comment_btn.innerHTML = "<span class='is-medium'>Comment</span>";
        let cancel = document.getElementById('labertasche-cancel-reply');
        if (cancel){
            cancel.remove();
        }
    }
}
