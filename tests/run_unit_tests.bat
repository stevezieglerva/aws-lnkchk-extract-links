cls

call ..\Scripts\activate
REM call python -m unittest unit_tests.py unit_tests_cache.py unit_tests_ESLambdaLog.py  unit_tests_LocalTime.py unit_tests_Link.py unit_tests_Page.py
call python unit_tests_Page.py

call deactivate
