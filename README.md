# aws-lnkchk-start
Detects S3 bucket updates to add a page to the queue


S3 -> 
	Lambda:aws-lnkchk-start 
		-> SQS:lnkchk-pages 
			-> Lambda:aws-lnkchk-extract-links 
				-> SQS:lnkchk-links 
					-> Lamba:aws-lnkchk-verify-links
						-> SNS:bad-links



