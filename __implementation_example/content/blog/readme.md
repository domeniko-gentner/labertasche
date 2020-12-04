---
title:  "Labertasche minimal implementation example"
date: 2020-12-03 09:00:00
categories: blog
---

This is a minimal example on how to implement Labertasche,
using Bulma CSS. The CSS is not that important, however, it
also shows how to utilize a modal dialogue to give your users
a good experience.

<!--more-->

## Setup

Please modify `mail_credentials.yaml` and make sure mail can be sent.
Everything else is set up. You can run flask with pycharm or on a local
server. It is up to you. I recommend using pycharm with the flask parameters
`--host=dev.localhost  --port=1314`. Make sure `dev.localhost` is in your
hosts file and resolves to `127.0.0.1`. This is necessary to set a cookie domain.
The server will not be able to run without.

## Where to start?

Start by reading `layouts/_default/baseof.html`. Notice the Javascript.
It has the default `labertasche.js` included and a custom file, where I
handle the callbacks. In production, you would concat these files using
the Hugo asset pipeline. I've left them separate, so you can see what is custom and what is included.

The next stop should be `single.html`. There you can find the first go block
needed, which adds the comments to each article in Hugo. Query for sections
if you want to exclude certain sections or only allow one, e.g. `blog`.

Last but not least, `comments.html` in the partials folder. This is where
basically all the magic happens. Read the javascript functions as they appear.
Basically, all I am doing is to query the DOM elements and adding/removing 
classes as I go, to display certain things. There is also a quick explanation further down.

**Please note**: This version has a modified reply function, so it displays the 
hidden field with the reply id. 
This does not occur on the production version, but can be helpful for debugging.

## Javascript functions explained

This is a quick and short explanation of all javascript functions. Yes, you may use and modify them.

### labertasche_text_counter()

This function counts the amount of characters put into the text area. This is purely cosmetic and only the first 
filter. If users have disabled Javascript, they could circumvent this, so the server checks lengths too.

### labertasche_validate_mail()

This checks if the entered text is a valid mail address, with a regex match. This does not check if the 
domain exists or if the mail is _really_ an email, but that is done server side. It's only used to minimize false 
requests. 

### labertasche_modal_hide()

This hides the modal dialog when the button on the modal is clicked.

### labertasche_comment_not_found()

When a comment is not valid, Labertasche will redirect to `dev.localhost?cnf=true`. This function shows a modal 
to inform the user about it. The JS for checking this parameter is in `baseof.html`.

### labertasche_comment_deleted()

Same as above, but with `dev.localhost?deleted=true`. This happens when a user deletes the comment via the link
sent by mail.

### labertasche_post_callback(state)

This is the callback used via the Labertasche post function. It simply displays different modals when certain error
codes are received. This is extremely useful, because you can inform your user about what is happening.

### labertasche_reply_callback(state, comment_id)

The callback for the reply callback. This does a little more, it displays a new button which the user can press to 
disable the reply and go to a parent comment. This is useful, because the user does not have to reload the site and
therefore, does not need to type it all again, if the reply was done in error.

## Feedback

Hope this example makes it more comfortable to use Labertasche, please send me a mail or open an issue if anything
is unclear. 

## Try it out!

Scroll down and comment. This is only locally. Please note: If livereload is enabled, you may not see all dialogs.
Turn livereload in Hugo off, if you want to see all of them:   
`--disableLiveReload`.

The example comments also will disappear when you comment, as they are not included in the database.