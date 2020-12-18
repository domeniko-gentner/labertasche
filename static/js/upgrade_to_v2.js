// # /**********************************************************************************
// #  * _author  : Domeniko Gentner
// #  * _mail    : code@tuxstash.de
// #  * _repo    : https://git.tuxstash.de/gothseidank/labertasche
// #  * _license : This project is under MIT License
// #  *********************************************************************************/

let base_url = window.location.protocol + "//" + window.location.host + '/upgrade/db_v2';

function mdi_message(message, success=true)
{
    let msgpane = document.getElementById('update-messages');
    let icon = document.createElement('i');
    icon.classList.add('mdi');
    icon.classList.add('mdi-24px');
    if (success){
        icon.classList.add('has-text-success');
        icon.classList.add('mdi-check-bold');
    }
    else {
        icon.classList.add('has-text-danger');
        icon.classList.add('mdi-alpha-x-box-outline');
    }

    let text = document.createElement('span');
    text.classList.add('has-text-white');
    text.innerHTML = "&nbsp;" + message

    msgpane.appendChild(icon);
    msgpane.appendChild(text);
    msgpane.appendChild(document.createElement('br'));
}

async function start_upgrade_to_v2()
{
    console.log('helo');
    let start_btn = document.getElementById('start-button');
    start_btn.remove();

    // Add progress bar instead of button
    let progressbar = document.createElement('progress');
    progressbar.setAttribute('value', '0');
    progressbar.setAttribute('max', '100');
    progressbar.classList.add('progress');
    progressbar.classList.add('is-medium');
    progressbar.classList.add('is-success');
    progressbar.innerHTML = '&nbsp;';
    document.getElementById('controls').appendChild(progressbar);

    let success;
    success = await backup();
    if(success){
        progressbar.setAttribute('value', '25');
        success = await export_db();
        if (success){
            progressbar.setAttribute('value', '50');
            success = await recreate_db();
            if (success){
                progressbar.setAttribute('value', '75');
                success = await import_db();
                progressbar.setAttribute('value', '100');
            }
        }
    }
    if (!success){
        progressbar.classList.remove('is-success');
        progressbar.classList.add('is-danger');
    }
    else{
        progressbar.remove();
    }

    // reset button
    start_btn.classList.remove('is-loading');
}

async function backup()
{
    let status = false;
    await fetch(base_url + "/backup/", {
        mode: "cors",
        headers: {
            'Access-Control-Allow-Origin': window.location.host,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        method: "GET"
    })
    .then(async function (response){
        let j = await response.json();
        if (j['status'] === 'ok'){
            mdi_message("Backup successfully created", true);
            status = true;
        }
        if (j['status'] === 'exception-write-json') {
            mdi_message(j['msg'], false)
            mdi_message("A server-side exception occured while writing the json, please check writing rights in the root directory.", true);
        }
        if (j['status'] === 'exception-copy-db') {
            mdi_message(j['msg'], false)
            mdi_message("A server-side exception occured while copying the database, please check writing rights in the root directory.", false);
        }
    })
    .catch(function (exc) {
        mdi_message(exc, false);
        mdi_message("An exception occured, please report this bug to code@tuxstash.de", false);
    });
    return status;
}


async function export_db()
{
    let status = false;
    await fetch(base_url + "/export/", {
        mode: "cors",
        headers: {
            'Access-Control-Allow-Origin': window.location.host,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        method: "GET"
    })
    .then(async function (response){
        let j = await response.json();
        if (j['status'] === 'ok'){
            mdi_message("Tables successfully exported", true);
            status = true;
        }
        if (j['status'] === 'exception') {
            mdi_message(j['msg'], false)
            mdi_message("A server-side exception occured.", false);
        }
    })
    .catch(function (exc) {
        mdi_message(exc, false);
        mdi_message("A Javascript exception occured, please report this bug to code@tuxstash.de", false);
    })
    return status
}


async function recreate_db()
{
    let status = false;
    await fetch(base_url + "/recreate/", {
        mode: "cors",
        headers: {
            'Access-Control-Allow-Origin': window.location.host,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        method: "GET"
    })
    .then(async function (response){
        let j = await response.json();
        console.log(j);
        if (j['status'] === 'ok'){
            mdi_message("Database deleted and recreated", true);
            status = true;
        }
        if (j['status'] === 'exception') {
            mdi_message(j['msg'], false)
            mdi_message("A server-side exception occured.", false);
        }
    })
    .catch(function (exc) {
        mdi_message(exc, false);
        mdi_message("A Javascript exception occured, please report this bug to code@tuxstash.de", false);
    })
    return status
}


async function import_db()
{
    let status = false;
    await fetch(base_url + "/import/", {
        mode: "cors",
        headers: {
            'Access-Control-Allow-Origin': window.location.host,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        method: "GET"
    })
    .then(async function (response){
        let j = await response.json();
        console.log(j);
        if (j['status'] === 'ok'){
            mdi_message("New tables preseeded and data imported. You may now return to the dashboard.", true);
            status = true;
        }
        if (j['status'] === 'exception-database') {
            mdi_message(j['msg'], false)
            mdi_message("An error occured while adding the data to the database.", false);
        }
        if (j['status'] === 'exception-filenotfound') {
            mdi_message(j['msg'], false)
            mdi_message("The exported files have not been found. Please check the file permissions.", false);
        }
    })
    .catch(function (exc) {
        mdi_message(exc, false);
        mdi_message("A Javascript exception occured, please report this bug to code@tuxstash.de", false);
    })
    return status
}
