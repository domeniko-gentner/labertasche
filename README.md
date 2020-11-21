# Labertasche

A comment system for Hugo, written in Python (and Javascript).

## Feature Set

* Written in Python, utilizing Flask
  * Robust Database handling by utilizing SQLAlchemy, which supports all big database engines
  * flask-cors for robust security
* Uses Javascript to send comment via POST to the comment server
  * Has callbacks for implementing your own notifications during the posting process.
* No IP being logged
* Email confirmation 
* EMail Blocklist 
* Only outputs JSON, so templates can be done independently, enhancing customization. Using the comments via a partial
  template in Hugo is the recommended way. See below for integration code.


## Requirements

* A public webserver capable of running Apache/NGINX and/or gunicorn. This server does not need to be the same as the 
  server running the site, but it must have access to your CI/CD chain. Same server is of course easier to implement.


## How does it work?

A picture often says more than a thousand words:

![flow chart image](/docs/flow-chart.png "Flow Chart")

In some words, the user sends the comment from your site to the comment system, the comment system does the validation
and confirmation. Then, a json is put into the data directory from where you can load it via Hugo and generate your 
template.

## Setup

Run `ssh://git@git.tuxstash.de:1235/gothseidank/labertasche.git` in the directory where you wish to host the comment 
system. For example, `/var/www/html`, I also recommend making use of `/srv/` or `/opt/`. It depends on you.

When everything is downloaded, create the directory `/etc/labertasche`. In this directory, we need 2 files:

* labertasche.yaml - you can find an example in the root directory.
* mail_credentials.json - you can find an example in the root directory.

Copy these files from the root directory of this app to the folder `/etc/labertasche`. Make sure to set ownership for 
your user that runs your server later. I always do `chmown user:www-data`, so Apache has only group rights and enable read-only 
for the Apache user.

Make sure to read the config and replace the values as needed. The mail configuration should need no explanation,
`labertasche.yaml` has comments. Feel free to bug about more documentation regarding this. Pay special attention to 
secrets and passwords.

Now, for the server there are several options. I personally always host flask apps with Apache and mod_wsgi. 
The config looks like this:

* [Apache](docs/apache-config.md)

Other options:

* [gunicorn](https://gunicorn.org/https://gunicorn.org/) + Apache/Nginx with Proxy Pass

Once you can see the administrative page, you can start integrating it into Hugo.

## Integrating it into Hugo

### Javascript

In the project folder is a small javascript file. You will need to load this into Hugo, I suggest using Hugo's asset 
pipeline to integrate it into your site. One thing is important to know: this script only does the bare bones post request 
to your comment backend. Anything else must be done by yourself, but don't worry: The function is making use of a callback, 
so you can control what happens during the various stages. 

TODO: Example using the javascript properly

### Hugo templates

Remember the `labertasche.yaml` file? It asked you where the data folder of Hugo is. What this program does, is to place
various json files into that folder, in folders that describe your sections. So, for each category/section of your blog
where comments can be placed, one folder will be made. And for each page within that section it generates a json file.

Now create a new partial called "comments.html" (or something else). Within that template the following structure is needed:

```
{{ $location := .Scratch.Get "location" }} 
{{ if (fileExists $location ) }}
    {{ $dataJ := getJSON  $location }}
        {{ range $dataJ.comments }}
                   
        {{ end }}
{{ end }}
```

This loads the json depending on the rel url and walks the list of comments. You can then use the following variables to 
access the per-comment data:  

* .content      => The body of the message the user has sent
* .email        => The mail the person used to send the mail
* .created_on   => The date and time the comment was posted
* .comment_id   => The comment id, great for making anchors
* .gravatar     => The md5 hash of the mail for gravatar, if caching is on, prepend e.g. `/images`, otherwise use the gravatar url to integrate it.

You can style around them as needed. You have free reign. 

Of course you will also need a few inputs and a button that submits the data.
Here is a base skeleton to start out:

```
<div>
    <input type="text" maxlength=100 placeholder="Enter Email" id="labertasche-mail">
    <textarea cols="10" rows="10" id="labertasche-text"></textarea>
    <input type="button" onclick="labertasche_post_comment(this, labertasche_callback);">
</div>
```

Please take note of the `id` on each element, these are mandatory, as well as the function call for the `onclick` event.
Again, style as needed and add more Javascript to your gusto.


Inside your template `single.html`, or wherever you want to place comments, you qwill also need this:
 
``` 
{{ $file := replaceRE "^(.*)[\\/]$" "data$1.json" .Page.RelPermalink }}
{{ .Scratch.Set "location" $file }}
{{ partial "partials/comments" . }}
```

After that and configuring labertasche correctly, the json files should be placed in your data folder and all you got
to do after that, is to rebuild Hugo and the new comment should appear. 


