// # /**********************************************************************************
// #  * _author  : Domeniko Gentner
// #  * _mail    : code@tuxstash.de
// #  * _repo    : https://git.tuxstash.de/gothseidank/labertasche
// #  * _license : This project is under MIT License
// #  *********************************************************************************/

function dashboard_mailsearch(search_txt)
{
    let el = document.getElementById('mail-table');
    let children = el.children;
    for (let i = 0; i < children.length; i++ )
    {
        children[i].style.display = "none";
        let iTxt = children[i].innerText.replace(/(\r\n|\n|\r)/gm, "").trim();

        if ( search_txt.value === iTxt.slice(0, search_txt.value.length)){
            children[i].style.display = "table-row";
        }
    }
}

function new_project_save() {
    let modal_ok = document.getElementById('modal-ok');
    let modal_cancel = document.getElementById('modal-cancel');
    let short_help = document.getElementById('new-project-too-short');
    let short_help_invalid = document.getElementById('new-project-invalid-name');
    let name = document.getElementById('project-name').value

    short_help.classList.add('is-hidden');
    short_help_invalid.classList.add('is-hidden');

    // Validate input
    if (name.length === 0) {
        short_help.classList.remove('is-hidden');
        return false;
    }
    if (/^\w+$/.test(name) === false){
        short_help_invalid.classList.remove('is-hidden');
        return false;
    }

    modal_ok.classList.add('is-loading');
    modal_cancel.classList.add('is-hidden');
    fetch(window.location.protocol + "//" + window.location.host + '/dashboard/project/new',
        {
            mode: "cors",
            headers: {
                'Access-Control-Allow-Origin': '*',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            method: "POST",
            // use real location
            body: JSON.stringify({
                "name": name
            })
        })
        .then(async function (response) {
            let result = await response.json();
            result = result['status'];
            modal_ok.classList.remove('is-loading');
            modal_cancel.classList.remove('is-hidden');
            if (result === "ok"){
                hide_modal('modal-new-project');
            }
            if (result === "too-short"){
                short_help.classList.remove('is-hidden');
            }
            if (result === "invalid-name"){
                short_help_invalid.classList.remove('is-hidden');
            }
        })
        .catch(function (exc) {
            console.log(exc);
        })
}

function hide_modal(id_name)
{
    let el = document.getElementById(id_name);
    el.classList.remove("is-active");
}

function show_modal(id_name)
{
    let el = document.getElementById(id_name);
    el.classList.add("is-active");
}
