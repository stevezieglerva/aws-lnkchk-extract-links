
call aws logs filter-log-events --log-group-name  /aws/lambda/aws-lnkchk-extract-links  --start-time 1530789980065  --filter-pattern "?Starting ?Processing ?Error ?Downloading ?Extracting ?Checking ?Checked ?Finished" > search_results.txt
call search_results.txt

