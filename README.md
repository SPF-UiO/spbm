SPFs "SPBM"
===========

Her er koden for SPF sitt nye nettbaserte system.

Denne versjonen er en særdeles sterkt omstrukturert og noenlunde oppdatert variant av Aleksis originale system fra 2014.

Før inn bugs i [bugtrackeren](https://bitbucket.org/Aleksi/spf/issues).


Getting started with i18n
-------------------------

1. Make sure to add strings using `ugettext` and similarly, such as `ugettext_lazy` in models. 
For more information, see Django's own documentation on how to mark strings as localiseable.

2. Once strings have been added, update the locales with the following combo.

    ```sh
    $ ./manage.py extract && ./manage.py merge
    ```
    
    This will extract all the localizable strings into `locale/templates`, followed by a merge with `locale/xx_XX`.
    Both `extract` and `merge` are provided by `puente`. **DO NOT USE DJANGO'S `makemessages`, EVER!**

3. Once you've translated the strings in `locale/xx_XX/django.po`, you'll want to *compile* the strings.
    You'll want to do this every time there's a deployment, but also when you're working locally. 
    
    ```sh 
    $ ./manage.py compilemessages
    ```

Deployment
----------
At the moment there's no *full* CI pipeline that takes care of deployment.

See `scripts/run_production.sh` for the most important steps that take place upon deployment.


Things to do
------------

*Simple list created at the SPF-meeting 15.03.16.*

### Pressing issues

* Users cannot be booked to events by other societies.
	* Causes issue for RF-regi people, as well as CYB with silly people like Nicolai that help too many people!


### Kill-Own-System Issues
* Start and end time must be possible to add. Must be for Event and Workers *separately*.
* Add information about who the loan was for, including billing information and more.
