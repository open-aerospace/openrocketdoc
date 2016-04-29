============
Installation
============

`openrocketdoc` can be installed from pypi like any other python package using pip. In the python community it's considered best practice to use virtual environments, so if you have many projects working at once they can each use their own copy of python packages.  If you have virtualenvwrapper installed::

    $ mkvirtualenv openrocketdoc
    $ pip install openrocketdoc

If you want to install globally for all users, and you have root access, you can run::

    $ sudo pip install openrocketdoc

Installing just for you might work too::

    $ pip install --user openrocketdoc

**Install from source**

First download the source, for instance clone the git repo from github:

    $ git clone https://github.com/open-aerospace/openrocketdoc.git

Then, again use a virtualenv if possible:

    $ mkvirtualenv openrocketdoc
    $ python setup.py install
