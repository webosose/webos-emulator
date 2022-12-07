=======================
webOS Emulator Launcher
=======================


.. image:: https://img.shields.io/pypi/v/webos-emulator.svg
        :target: https://pypi.python.org/pypi/webos-emulator


webos-emulator(webOS Emulator Launcher) is a utility tool for launching various webOS Emulators and provides simple and fast environment settings.

* Documentation: https://webosose.org/docs/tools/sdk/emulator/virtualbox-emulator/emulator-launcher/

Features
--------

* Emulator creation for pre-defined profile
* Configurable emulator settings for various options
* Launching and Deleting the chosen emulator

Quickstart
----------

Install the latest webos-emulator if you haven't installed it yet

    python3 -m pip install --upgrade webos-emulator --force-reinstall

Generate a webOS OSE emulator with a vmdk file

    webos-emulator -vd ose_516 -c -i webos-image-qemux86-64-master-516.wic.vmdk

Then launch the emulator

    webos-emulator -vd ose_516 -s



Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
