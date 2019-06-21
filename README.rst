===============================================
postman2runner
===============================================


Convert postman data to JSON testcases for HttpRunner.

usage
================
To see ``postman2runner`` version:

.. code:: shell

    $ python main.py -V
    0.1.0




To see available options, run
==========================================

.. code:: shell

    $ python main.py -h
    usage: main.py [-h] [-V] [--log-level LOG_LEVEL]
               [postman_testset_file] [output_testset_file]

    Convert postman testcases to JSON testcases for HttpRunner.

    positional arguments:
        postman_testset_file  Specify postman testset file.
        output_testset_file   Optional. Specify converted JSON testset file.

    optional arguments:
        -h, --help            show this help message and exit
        -V, --version         show version
        --log-level LOG_LEVEL
                        Specify logging level, default is INFO.



examples
=============

In most cases, you can run ``postman2runner`` like this:github.com/maraujop/django-crispy-forms

.. code:: shell

    $ python3 main.py test/test.json  --output_dir tests/output --output_file_type yaml
    INFO:root:Generate JSON testset successfully: output.json

As you see, the first parameter is postman source file path, and the second is converted JSON file path.

The output testset file type is detemined by the suffix of your specified file.

If you only specify postman source file path, the output testset is in JSON format by default and located in the same folder with source file.

.. code:: shell

    $ python3 main.py test/test.json
    INFO:root:Generate JSON testset successfully: output.json

generated testset
=================

generated JSON testset ``output.json`` shows like this:

.. code:: json

    [
        {
            "test": {
                "name": "/api/v1/Account/Login",
                "request": {
                    "method": "POST",
                    "url": "https://httprunner.top/api/v1/Account/Login",
                    "headers": {
                        "Content-Type": "application/json"
                    },
                    "json": {
                        "UserName": "test001",
                        "Pwd": "123",
                        "VerCode": ""
                    }
                },
                "validate": []
            }
        }
    ]


Authors
========

- Author : gerrywen
- Email : blog@gerrywen.com

Documentation
=============

待续...

Note
=====

待续...

