//**********************************************************************************
//  * _author  : Domeniko Gentner
//  * _mail    : code@tuxstash.de
//  * _repo    : https://git.tuxstash.de/gothseidank/labertasche
//  * _license : This project is under MIT License
//  *********************************************************************************/

/*
    Callback example.
    Possible messages:

    post-min-length
    post-max-length
    post-invalid-json
    post-duplicate
    post-internal-server-error
    post-success
    post-before-fetch

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
*/

function labertasche_post_comment(btn, callback)
{
    let remote = document.getElementById('labertasche-comment-section').dataset.remote;
    let comment = document.getElementById('labertasche-text').value;
    let mail = document.getElementById('labertasche-mail').value;

    if (mail.length <= 0 || comment.length < 40){
        callback('post-min-length');
        if(btn) {
            btn.preventDefault();
        }
        return
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
                "replied_to": null  // TODO: future feature: replies?
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
