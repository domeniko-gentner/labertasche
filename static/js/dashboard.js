// # /**********************************************************************************
// #  * _author  : Domeniko Gentner
// #  * _mail    : code@tuxstash.de
// #  * _repo    : https://git.tuxstash.de/gothseidank/labertasche
// #  * _license : This project is under MIT License
// #  *********************************************************************************/

async function get(partial, callback = null, accept_lang = null) {

    let headers = {
        'Access-Control-Allow-Origin': window.location.host,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
    }
    if (accept_lang){
        headers = Object.assign(headers, {'Accept-Language': accept_lang})
    }

    return await fetch(window.location.protocol + "//" + window.location.host + partial,
    {
            mode: "cors",
            headers,
            method: "GET"
        })
        .then(async function (response) {
            const result = await response.json();
            if (callback){ callback(result); }
            return result;
        })
        .catch(function (exc) {
            console.log(exc);
            return null;
        })
}

async function post(partial, stringified_json, callback = null) {
    return await fetch(window.location.protocol + "//" + window.location.host + partial,
    {
            mode: "cors",
            headers: {
                'Access-Control-Allow-Origin': window.location.host,
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            method: "POST",
            body: stringified_json
        })
        .then(async function (response) {
            const result = await response.json();
            if (callback){ callback(result); }
            return result;
        })
        .catch(function (exc) {
            console.log(exc);
            return null;
        })
}

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

        if (iTxt.includes(search_txt.value)){
            children[i].style.display = "table-row";
        }
        if(search_txt.value === ''){
            children[i].style.display = "table-row";
        }
    }
}

// ------------------------------------------------------
// Deletes a project from the db
// ------------------------------------------------------
async function project_delete()
{
    let modal = document.getElementById('modal-project-delete');
    let modal_ok = document.getElementById('modal-delete-ok');
    let modal_cancel = document.getElementById('modal-delete-cancel');

    const project = modal.dataset.name;
    if (project === null || project.length === 0){
        console.log("Couldn't find a valid dataset");
        return;
    }

    modal_ok.classList.add('is-loading');
    modal_cancel.classList.add('is-hidden');

    await get('/api/project/delete/' + project, function(result){
        modal_ok.classList.remove('is-loading');
        modal_cancel.classList.remove('is-hidden');
        if (result === "ok") {
            console.log(result);
        }
    })
    modal.classList.remove('is-active');
    window.location.reload(true);
}

// ------------------------------------------------------
// Hides any modal
// ------------------------------------------------------
function hide_modal(id_name, redirect=null)
{
    let el = document.getElementById(id_name);
    el.classList.remove("is-active");

    if(redirect != null){
        window.location = redirect;
    }
}


// ------------------------------------------------------
// Shows any modal and attach project name
// ------------------------------------------------------
function show_modal(id_name, proj_name)
{
    let el = document.getElementById(id_name);
    el.classList.add("is-active");
    el.setAttribute('data-name', proj_name);
}

// ------------------------------------------------------
// Shows edit/new modal
// ------------------------------------------------------
async function show_modal_with_project(id_name, proj_name)
{
    // Get title element
    let title = document.getElementById('modal-title');

    // Get Dialog
    let modal = document.getElementById(id_name);

    // Load i18n
    let i18n = await get('/api/language', null, document.body.dataset.language);

    if (proj_name){
        // Get Data
        await get('/api/project/get/' + proj_name,
            function(r){
            document.getElementById('edit-project-blog-url').value = r['blogurl'];
            document.getElementById('edit-project-output').value = r['output'];
            document.getElementById('edit-project-gravatar-cache').checked = r['gravatar_cache'];
            document.getElementById('edit-project-gravatar-cache-dir').value = r['gravatar_cache_dir'];
            document.getElementById('edit-project-gravatar-size').value = r['gravatar_size'];
            document.getElementById('edit-project-send-otp').checked = r['sendotp'];
            document.getElementById('edit-project-addons-smileys').checked = r['addon_smileys'];
        });

        // Set project name
        let proj_el = document.getElementById('edit-project-name');
        proj_el.value = proj_name

        // Set project name
        title.innerText =i18n['javascript_edit_project_modal_title'].replace('%name%', proj_name);

        // Make active
        modal.classList.add("is-active");

        // Edit mode
        modal.setAttribute('data-mode', 'edit');
        modal.setAttribute('data-name', proj_name);
    }
    if (proj_name == null){
        // Set project name
        title.innerText = i18n['new_project'];

        // Reset fields, needed when user pressed cancel on edit modal
        document.getElementById('edit-project-name').value = "";
        document.getElementById('edit-project-blog-url').value = "";
        document.getElementById('edit-project-output').value = "";
        document.getElementById('edit-project-gravatar-cache').checked = true;
        document.getElementById('edit-project-gravatar-cache-dir').value = "";
        document.getElementById('edit-project-gravatar-size').value = 256;
        document.getElementById('edit-project-send-otp').checked = true;
        document.getElementById('edit-project-addons-smileys').checked = true;

        // Edit mode
        modal.setAttribute('data-mode', 'new');

        // Make active
        modal.classList.add("is-active");
    }
}

async function save_project_settings(id_name)
{
    // Spin the tea cups
    let btn = document.getElementById('modal-save-ok');
    btn.classList.add('is-loading');

    // Get modal
    let modal = document.getElementById(id_name);

    // Get field data
    let json_data = {
        "name": document.getElementById('edit-project-name').value,
        "blogurl":  document.getElementById('edit-project-blog-url').value,
        "output": document.getElementById('edit-project-output').value,
        "gravatar_cache": document.getElementById('edit-project-gravatar-cache').checked,
        "gravatar_cache_dir": document.getElementById('edit-project-gravatar-cache-dir').value,
        "gravatar_size": document.getElementById('edit-project-gravatar-size').value,
        "sendotp": document.getElementById('edit-project-send-otp').checked,
        "addon_smileys": document.getElementById('edit-project-addons-smileys').checked
    }

    // Get field for errors and reset it
    let error = document.getElementById('modal-edit-error-messages')
    error.innerText = ''
    let has_error = false;

    if (modal.dataset.mode === "edit"){
        let old_name = modal.dataset.name;
        await post('/api/project/edit/' +  old_name, JSON.stringify(json_data), function(result){
            if (result['status'] !== 'ok') {
                has_error = resolve_error_status(error, result);
            }
        })
    }
    if (modal.dataset.mode === 'new'){
        await post('/api/project/new', JSON.stringify(json_data), function(result){
            if (result['status'] !== 'ok') {
                has_error = resolve_error_status(error, result);
            }
        })
    }

    // Reset button
    btn.classList.remove('is-loading');
    if (has_error === false){
        window.location.reload(true);
    }
}

// ------------------------------------------------------
// Disables inputs when gravatar caching is disabled.
// ------------------------------------------------------
function toggle_gravatar_settings(chkbx)
{
    let cache = document.getElementById('edit-project-gravatar-cache-dir');
    let size = document.getElementById('edit-project-gravatar-size');

    if(!chkbx.checked){
        cache.setAttribute('disabled', '');
        size.setAttribute('disabled', '');
        cache.value = "disabled";
        size.value = "disabled";
    }
    else{
        cache.removeAttribute('disabled');
        size.removeAttribute('disabled');
        cache.value = "";
        size.value = "256";
    }
}

// ------------------------------------------------------
// Exports all comments
// ------------------------------------------------------
async function export_all_comments(btn)
{
    btn.classList.add('is-loading');
    let proj_name = document.getElementById('modal-comments-export').dataset.name;
    let result = await get('/api/comment-export-all/' + proj_name);

    if (result['status'] === 'ok'){
        hide_modal('modal-comments-export');
    }
    if (result['status'] === 'not-found'){
        // Redirect to error
        hide_modal('modal-comments-export', '?error=404');
    }

    // Reset button
    btn.classList.remove('is-loading');
    console.log(result);
}


async function resolve_error_status(field, result)
{
    // Load i18n
    let i18n = await get('/api/language', null, document.body.dataset.language);

    let has_error = false;

    if (result['status'] === 'too-short'){
        field.innerText = i18n['javascript_required_field_empty'];
        has_error = true;
    }
    if (result['status'] === 'invalid-project-name') {
        field.innerText = i18n['javascript_invalid_project_name'];
        has_error = true;
    }
    if (result['status'] === 'project-exists') {
        field.innerText = i18n['javascript_project_duplicate'];
        has_error = true;
    }
    if (result['status'] === 'invalid-blog-url') {
        field.innerText = i18n['javascript_blogurl_invalid'];
        has_error = true;
    }
    if (result['status'] === 'invalid-path-output') {
        field.innerText = i18n['javascript_output_nonexistent'];
        has_error = true;
    }
    if (result['status'] === 'invalid-path-cache') {
        field.innerText = "The cache path does not exist!";
        has_error = true;
    }
    if (result['status'] === 'exception') {
        field.innerText = i18n['javascript_exception'];
        field.innerText += "\n" + result['msg'];
        has_error = true;
    }
    return has_error;
}
