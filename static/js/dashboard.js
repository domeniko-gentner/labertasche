// # /**********************************************************************************
// #  * _author  : Domeniko Gentner
// #  * _mail    : code@tuxstash.de
// #  * _repo    : https://git.tuxstash.de/gothseidank/labertasche
// #  * _license : This project is under MIT License
// #  *********************************************************************************/

// ------------------------------------------------------
// Called when search for mail addresses in manage mail
// ------------------------------------------------------
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

// ------------------------------------------------------
// Called when a new project is created,
// posts it to the server
// ------------------------------------------------------
function new_project_save() {
    let modal_ok = document.getElementById('modal-ok');
    let modal_cancel = document.getElementById('modal-cancel');
    let short_help_short = document.getElementById('new-project-too-short');
    let short_help_invalid = document.getElementById('new-project-invalid-name');
    let name = document.getElementById('project-name').value

    short_help_short.classList.add('is-hidden');
    short_help_invalid.classList.add('is-hidden');

    // Validate input
    if (name.length === 0) {
        short_help_short.classList.remove('is-hidden');
        return false;
    }
    if (/^\w+$/.test(name) === false){
        short_help_invalid.classList.remove('is-hidden');
        return false;
    }

    modal_ok.classList.add('is-loading');
    modal_cancel.classList.add('is-hidden');
    fetch(window.location.protocol + "//" + window.location.host + '/api/project/new',
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
                window.location.reload(true);
            }
            if (result === "too-short"){
                short_help_short.classList.remove('is-hidden');
            }
            if (result === "invalid-name"){
                short_help_invalid.classList.remove('is-hidden');
            }
        })
        .catch(function (exc) {
            console.log(exc);
        })
}

function project_delete()
{
    let modal = document.getElementById('modal-project-delete');
    let modal_ok = document.getElementById('modal-delete-ok');
    let modal_cancel = document.getElementById('modal-delete-cancel');

    const project = modal.dataset.project;
    console.log("Project: " + project);
    if (project === null || project.length === 0){
        console.log("Couldn't find a valid dataset");
        return;
    }

    modal_ok.classList.add('is-loading');
    modal_cancel.classList.add('is-hidden');
    fetch(window.location.protocol + "//" + window.location.host + '/api/project/delete/' + project,
        {
            mode: "cors",
            headers: {
                'Access-Control-Allow-Origin': '*',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            method: "GET"
        })
        .then(async function (response) {
            let result = await response.json();
            result = result['status'];
            modal_ok.classList.remove('is-loading');
            modal_cancel.classList.remove('is-hidden');
            if (result === "ok") {
                hide_modal('modal-project-delete');
                window.location.reload(true);
            }
            console.log(result);
        })
        .catch(function (exc) {
            console.log(exc);
        })
}



// ------------------------------------------------------
// Hides any modal
// ------------------------------------------------------
function hide_modal(id_name)
{
    let el = document.getElementById(id_name);
    el.classList.remove("is-active");
}

// ------------------------------------------------------
// Shows any modal
// ------------------------------------------------------
function show_modal(id_name)
{
    let el = document.getElementById(id_name);
    el.classList.add("is-active");
}

// ------------------------------------------------------
// Shows any modal
// ------------------------------------------------------
function show_modal_with_project(id_name, proj_name)
{
    let el = document.getElementById(id_name);
    el.classList.add("is-active");
    el.setAttribute('data-project', proj_name)
}
