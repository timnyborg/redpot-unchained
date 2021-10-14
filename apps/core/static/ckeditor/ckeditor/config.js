/* global CKEDITOR */
"use strict";
// Adds additional runtime settings to django-ckeditor's default (empty) config
// All other configuration should go in settings.py
CKEDITOR.editorConfig = function( config ) {
    // Define changes to default configuration here. For example:
    // config.language = 'fr';
    // config.uiColor = '#AADC6E';
};

// Allows an element to have no content (fontawesome icons)
// todo: may be possible to remove this upon implementing the FontAwesome5 plugin
CKEDITOR.dtd.$removeEmpty.span = false;
