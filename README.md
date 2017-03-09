SPFs "SPBM"
===========

Her er koden for SPF sitt nye nettbaserte system.

Denne versjonen er en særdeles sterkt omstrukturert og veldig--forhåpentligvis--oppdatert variant av Aleksis originale system fra 2014. 

For funksjonalitetsønsker m.m. kan du ta kontakt via e-postlisten, eller registrere et ønske via issue-behandleren.

*The rest of this document is in English.*

Contributing
------------
Any help is much appreciated. Take a look at our issues in the [issue tracker], and go crazy.

Hacking away
------------
### Getting started with i18n


1. Make sure to add strings using `ugettext` and similarly, such as `ugettext_lazy` in models. 
   For more information, see Django's own documentation on how to mark strings as localiseable.

2. Once strings have been added, update the locales with the following combo.

    ```sh
    $ ./manage.py extract && ./manage.py merge
    ```
    
    This will extract all the localizable strings into `locale/templates`, followed by a merge with `locale/xx_XX`.
    Both `extract` and `merge` are provided by `puente`.  
    :warning: **Do not use Django's `makemessages`!**

3. Once you've translated the strings in `locale/xx_XX/django.po`, you'll want to *compile* the strings.
    You'll want to do this every time you're working locally and you want to see the changes. 
    
    ```sh 
    $ ./manage.py compilemessages
    ```

### Deployment
See `scripts/run_production.sh` for the most important steps that take place upon deployment. 
This is combined with the awesome power of our `werker.yml` file, which is our CI of choice as of today.

[issue tracker]: https://github.com/SPF-UiO/spbm/issues
