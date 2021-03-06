SPFs "SPBM"
===========

[![Build Status](https://dev.azure.com/thoor/SPBM/_apis/build/status/SPF-UiO.spbm?branchName=master "Azure Pipelines status")](https://dev.azure.com/thoor/SPBM/_build/latest?definitionId=1&branchName=master)
[![coverage status](https://coveralls.io/repos/github/SPF-UiO/spbm/badge.svg?branch=master "Test coverage status")](https://coveralls.io/github/SPF-UiO/spbm?branch=master)
[![Maintainability](https://api.codeclimate.com/v1/badges/51ad586a4da8782c4834/maintainability "CodeClimate maintainability score")](https://codeclimate.com/github/SPF-UiO/spbm/maintainability)
[![Code quality](https://api.codacy.com/project/badge/Grade/0a368fd542fe42c29c55949db38428a3 "Codacy quality score")](https://www.codacy.com/gh/SPF-UiO/spbm)

Her er koden for *Studentkjellernes personalforening* sitt nåværende nettbaserte system for grovhåndtering av diverse utlån og leier av lokaler, studentansatte, fakturering av medlemsforeninger, samt lønnsrapportering for utbetaling av lønn.  
*This is the code for the *Student basement pubs society* current web-based system for roughly managing our various bookings and rentals of our collective premises, student employees, invoicing our member societies, as well as wage reporting to facilitate payroll.*

For funksjonalitetsønsker, problemer, og spørsmål kan du [opprette et issue her på GitHub][new issue].  
*For feature requests, problems, and questions, please [create an issue here on GitHub][new issue].*


## Getting Started

You need *Docker* and *Docker Compose* to get started locally. You may use *Docker* on its own, but it'll require setting the containers up manually.

To get started with a Gunicorn-based development environment with live reloads use `docker-compose`:

```sh
$ docker-compose up
```

You'll get a local development environment with SPBM, NGINX and PostgreSQL (available at [`localhost:80`](http://localhost:80)).

If you'd rather use the built-in Django development server (at [`localhost:8000`](http://localhost:8000)) you may do so.

```sh
$ docker-compose run spbm ./manage.py runserver 0.0.0.0:8000
```

Use `docker-compose` to perform other typical things while developing, such as migrating or loading.

```sh
$ docker-compose run spbm ./manage.py showmigrations --plan
$ docker-compose run spbm ./manage.py migrate
$ docker-compose run spbm ./manage.py loaddata User SpfUser Society Invoice Worker Employment Event NorlonnReport Shift
$ docker-compose run spbm ./manage.py ...
```

You may also use *Poetry* and a *virtualenv* for smoother development, but be careful and test your changes using the Docker container too to ensure that everything works the way it should.

### Production

Make sure to override default environment variables for SPBM, and PostgreSQL if you're using Docker Compose.

```sh
$ docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
```

### Translations and i18n

1. Make sure to add strings using `ugettext` and similarly, such as `ugettext_lazy` in models. 
   For more information, see Django's own documentation on how to mark strings as localiseable.

2. Once strings have been added in the code, extract and combine the strings into the locale's `PO` files:

    ```sh
    $ ./manage.py extract && ./manage.py merge
    ```
    
    This will extract all the localizable strings into `locale/templates`, followed by a merge with `locale/xx_XX`.
    Both `extract` and `merge` are provided by `puente`.  
    *Do not use Django's `makemessages`!*

3. Once you've translated the strings in `locale/xx_XX/django.po`, you'll want to *compile* the strings.
    You'll want to do this every time you're working locally and you want to see the changes. 
    
    ```sh 
    $ ./manage.py compilemessages
    ```


Contributing
------------

Any help is much appreciated. Take a look at our issues in the [issue tracker], and go crazy.

[issue tracker]: https://github.com/SPF-UiO/spbm/issues
[new issue]: https://github.com/SPF-UiO/spbm/issues/new
