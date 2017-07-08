SPFs "SPBM"
===========

[![build status](https://app.wercker.com/status/9957a592aed9cbb25f335978dfa7ae44/m/master "wercker status")](https://app.wercker.com/project/byKey/9957a592aed9cbb25f335978dfa7ae44)
[![coverage status](https://coveralls.io/repos/github/SPF-UiO/spbm/badge.svg?branch=master "coverage status")](https://coveralls.io/github/SPF-UiO/spbm?branch=master)

Her er koden for *Studentkjellernes personalforening* sitt nåværende nettbaserte system for grovhåndtering av diverse utlån og leier av lokaler, studentansatte, fakturering av medlemsforeninger, samt lønnsrapportering for utbetaling av lønn.  
*This is the code for the *Student basement pubs society* current web-based system for roughly managing our various bookings and rentals of our collective premises, student employees, invoicing our member societies, as well as wage reporting to facilitate payroll.*

For funksjonalitetsønsker, problemer, og spørsmål kan du [opprette et issue her på GitHub][new issue].  
*For feature requests, problems, and questions, please [create an issue here on GitHub][new issue].*


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
[new issue]: https://github.com/SPF-UiO/spbm/issues/new
