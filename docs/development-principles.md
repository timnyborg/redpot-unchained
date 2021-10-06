## 12 Factor design
See [https://12factor.net](https://12factor.net)

 * No credentials should be stored in the source code.  Instead, they should come from Environment Variables or secrets files.  Act like the source code is public, because it is.
 * No configuration should be stored in the source code.  Hosts, ports, service urls, etc., should come from Environment Variables or secrets files.  You should be able to switch any connected resource (database, cache, file server, APIs, etc.) without editing the source code.  We use the `environs` library to access secrets in `settings.py`, with defaults that allow Docker-based automated testing to function.
 * All python dependencies should go in `requirements.txt`.  Fetching them on a new environment should be as simple as `pip install -r requirements.txt`
 * All debian dependencies should go in `dependencies.txt`.  When deploying to a new environment, you shouldn't need to look through pip install errors to figure out what you're missing.

## Smallish apps
To separate concerns, and to keep models and views manageable, each app should be concerned with one class of object and its dependencies (e.g. Student, Module, Tutor, Programme, Invoice, Contract).

You may wind up with more imports, but it'll be easier to find what you're looking for once there's a form for every model object.

## DRY
Where you find yourself doing the same thing over and over in different apps generalize it and put it in the `core` app.
Including:

 * Mixins for Classes, Forms, Models, etc.
 * Custom-defined Views, Validators, FieldTypes, FormFields, abstract Models,
 * Templates, sub-templates, template tags, template filters
 * Model Managers for common filters (e.g. queries using is_active)

## Testing at all levels
 * Write unit tests for validators, tags, etc.
 * Write unit tests or simple integration tests for models, views, forms, etc., using model factories instead of depending on previous tests
 * Use Selenium where required (e.g. javascript, UI/UX-testing).

## GET requests should be read-only
See [https://twitter.com/rombulow/status/990684463007907840](https://twitter.com/rombulow/status/990684463007907840)

A GET request should never change the model's state.  So endpoints like `programme/remove-module/` or `module/publish/`
should only respond to POSTs.

This can be done through confirmation forms (e.g. an UpdateView or DeleteView, bootstrap
modals), javascript, or a host of other approaches.
