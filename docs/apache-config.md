This is an example server config for Apache Webserver with mod_wsgi.
If you wish to use pipenv, then please take also a look at the 
[WSGIPythonHome](https://modwsgi.readthedocs.io/en/develop/configuration-directives/WSGIPythonHome.html) 
directive.

```
<VirtualHost *:80>
    ServerAdmin server@example.com
    ServerName comments.example.com
    Redirect permanent / https://comments.example.com
</VirtualHost>


<VirtualHost *:443>
    ServerAdmin server@example.com
    ServerName comments.example.com

    WSGIDaemonProcess laberflask user=user group=group threads=2
    WSGIScriptAlias / /var/www/html/labertasche/server.wsgi

    SSLCertificateFile /etc/letsencrypt/live/comments.example.com/fullchain.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/comments.example.com/privkey.pem
    Include /etc/letsencrypt/options-ssl-apache.conf

    <Directory "/var/www/html/labertasche">
            WSGIProcessGroup laberflask
            WSGIApplicationGroup %{GLOBAL}
            Options -Indexes
            AllowOverride None
            Require all granted
    </Directory>
    ErrorLog ${APACHE_LOG_DIR}/laberflask.error.log
    CustomLog /dev/null common
</VirtualHost>
```
