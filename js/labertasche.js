//**********************************************************************************
//  * _author  : Domeniko Gentner
//  * _mail    : code@tuxstash.de
//  * _repo    : https://git.tuxstash.de/gothseidank/labertasche
//  * _license : This project is under MIT License
//  *********************************************************************************/

/*

//Callback example for post. Possible messages:
// post-min-length
// post-max-length
// post-invalid-json
// post-duplicate
// post-internal-server-error
// post-success
// post-before-fetch
function labertasche_callback(state)
{
    if (state === "post-before-fetch"){

    }
    if (state === "post-min-length"){

    }
    if (state === "post-success"){

    }
    if (state === "post-fetch-exception" || state === "post-internal-server-error"){

    }
    if (state === "post-invalid-email"){

    }
}

// Callback for initiating and cancelling replies.
// Posstible message: 'on' and 'off'
function labertasche_reply_callback()
{
    if (state === "on"){
    }

    if (state === "off"){
    }
}

*/

function labertasche_reply_to(comment_id, callback)
{
    let comments = document.getElementById('labertasche-comment-section');
    if (comments){
        if (document.getElementById('labertasche-replied-to')){
            document.getElementById('labertasche-replied-to').remove();
            callback('off', comment_id);
            if (comment_id === -1){
                return false;
            }
        }
        let reply = document.createElement("input");
        reply.setAttribute("type", "text");
        reply.setAttribute("id", "labertasche-replied-to");
        reply.classList.add("is-hidden");
        reply.value = comment_id;
        comments.appendChild(reply);
        callback('on', comment_id);
    }
    else{
        console.log("Missing text input with id labertasche-comment-section");
    }
}

function labertasche_post_comment(btn, callback)
{
    let remote = document.getElementById('labertasche-comment-section').dataset.remote;
    let comment = document.getElementById('labertasche-text').value.trim();
    let mail = document.getElementById('labertasche-mail').value.trim();
    let reply = document.getElementById('labertasche-replied-to');

    if (mail.length <= 0 || comment.length < 40){
        callback('post-min-length');
        if(btn) {
            return false;
        }
        return false;
    }

    callback('post-before-fetch');
    fetch(remote,
        {
            mode:"cors",
            headers: {
                'Access-Control-Allow-Origin':'*',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            method: "POST",
            // use real location
            body: JSON.stringify({ "email": mail,
                "content": comment,
                "location": window.location.pathname,
                "replied_to": reply.value
            })
        })
        .then(async function(response){
            let result = await response.json();
            callback(result['status']);
        })
        .catch(function(exc){
            console.log(exc);
            callback('post-fetch-exception');
        })

    // Don't reload the page
    return false;
}
