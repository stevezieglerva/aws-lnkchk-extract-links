cls
call ..\Scripts\activate
call python -m unittest integration_tests.py
call deactivate
