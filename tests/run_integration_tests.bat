cls
call ..\Scripts\activate
call python -m unittest integration_tests.py
call deactivate
call aws sqs receive-message --queue-url https://queue.amazonaws.com/112280397275/lnkchk-pages --attribute-names All --message-attribute-names All --output json

