set function_name=aws-lnkchk-extract-links

REM Zip the lambda function
call del /q lambda_function.zip
call "c:\Program Files\7-Zip\7z.exe" a lambda_function.zip *.py

REM Upload the new code
call aws lambda update-function-code --function-name %function_name% --zip-file fileb://lambda_function.zip

REM Call the function
call aws lambda invoke --function-name %function_name% --payload file://test_payload.json test_result.txt
call type test_result.txt

