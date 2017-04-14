This directory contains views exposed by Core api. To add new, just create new directory here. Each directory in
views should be python module. It means, that it should contain __init__.py file. To see example, look inside the api
directory. Important thing is to add imports of all functions into __init__.py. This allows to automatic discover of
functions in all API modules.

To expose function from your new module in API, decorate it by @api_log, @user_log or @ci_log. For details refer to
OverCluster documentation at http://cloudover.org/overcluster/. If you need to expose your finctions not in Core API,
see the CoreDav addition, which adds new functions and creates new Apache vhost for webdav service.

If creating new API extension, remember to list this extension in config.py in list LOAD_API