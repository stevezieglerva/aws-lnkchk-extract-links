call aws s3 sync  ./lnkchk-simple-site-integration s3://lnkchk-simple-site-integration/ --delete
call aws s3 sync  ./lnkchk-complex-site-integration s3://lnkchk-complex-site-integration/ --delete
call aws s3 sync  ./lnkchk-100-pages s3://lnkchk-100-pages/ --delete
pause