cls

call ..\Scripts\activate
call python -m unittest unit_tests.py unit_tests_cache.py unit_tests_ESLambdaLog.py 
call deactivate
