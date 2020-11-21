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
