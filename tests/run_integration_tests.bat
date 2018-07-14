cls

call aws dynamodb delete-table --table-name lnkchk-cache
REM Wait for table delete to complete and name be available again
timeout 30

call aws dynamodb create-table --table-name lnkchk-cache --key-schema AttributeName=url,KeyType=HASH --stream-specification StreamEnabled=True,StreamViewType=NEW_AND_OLD_IMAGES --attribute-definitions AttributeName=url,AttributeType=S --provisioned-throughput ReadCapacityUnits=10,WriteCapacityUnits=5
timeout 30

call aws dynamodb update-time-to-live --table-name lnkchk-cache --time-to-live-specification Enabled=True,AttributeName=ttl_epoch
call aws application-autoscaling register-scalable-target --service-namespace dynamodb --resource-id "table/lnkchk-cache" --scalable-dimension "dynamodb:table:ReadCapacityUnits" --min-capacity 5 --max-capacity 100
call aws application-autoscaling put-scaling-policy --service-namespace dynamodb --resource-id "table/lnkchk-cache" --scalable-dimension "dynamodb:table:ReadCapacityUnits" --policy-name "CacheScalingPolicy" --policy-type "TargetTrackingScaling"     --target-tracking-scaling-policy-configuration file://dynamodb_autoscaling_policy.json


call ..\Scripts\activate
call python -m unittest integration_tests.py
call deactivate
