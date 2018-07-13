cls
call run_unit_tests.bat > results.txt
call run_integration_tests.bat >> results.txt

call findstr "Ran" results.txt

