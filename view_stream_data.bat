echo on
echo list the shards of the stream
call aws dynamodbstreams describe-stream --stream-arn "arn:aws:dynamodb:us-east-1:112280397275:table/lnkchk-queue/stream/2018-06-17T02:35:39.488" --output json

echo getting a shard iterator based on a specific shard
call aws dynamodbstreams get-shard-iterator --stream-arn "arn:aws:dynamodb:us-east-1:112280397275:table/lnkchk-queue/stream/2018-06-17T02:35:39.488" --shard-id shardId-00000001529230624740-65f7b591 --shard-iterator LATEST --output text > shard_iterator.txt

REM echo set the shard iterator to an env variable
REM set /p shard_iterator=<shard_iterator.txt
REM echo %shard_iterator%

call set shard_iterator="arn:aws:dynamodb:us-east-1:112280397275:table/lnkchk-queue/stream/2018-06-17T02:35:39.488|1|AAAAAAAAAAGDG9LQAqtOxnpq4B3iTDi/bdpFPdAraCp6Yoy4LVeLeSPI7daOrjlILeczI5OBpCAIe9tD6sdDk0ADWpAj053+TrZ1FcakMpeRzGwEW6IjvOL+3F4jQ1sHj/BqkORyssi3hjVnG2dOqG4oNpTaIC21lJqLJCWBHzCcrkG+qB/L8oVUVF8x5x51Mbv9BfP+hSoDwpB9XeFjuPy5N7ic2JQU4H1/L++SNhkIxfnuvwEcZ5z2AXNo3VrNNpcc7yDoo1JAszkV1o8gJsfNxtNWveoKWfJcbfdXtTk/UPAHxs8u9gC456+YfiJGk8mvpvNijZYVe0fWXAoxhRwZ+J6QzBx0VdlEWs3JB332oeeywzYsdah60dmVhonwzUW9kSWrA9k80XZBt4+YgJcRRISdiDOomub9iHC3wDIHVG+zDKocOxFo4wU4YXMA3kjsVcU6V9buAlopMa9QzhM27sPWf5WlQ/+WK7cL6OY3hd4xyH/y72keSJ8nLOTVELUNzUqcs8Uz3w6DRF8qlDl8CMa7rjqJTvafRUPXnlnwbkZ2nZT0ZeUZIZnbHT2/fPZO4avWiEHaECeOn7AyT8eIRCtmYxzYWtetZXLPViU7Yx55fHkPdg=="
echo %shard_iterator%

echo Getting records 
call aws dynamodbstreams get-records --shard-iterator %shard_iterator% --output json


