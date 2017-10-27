# Introduction

The campaign contributions published by Federal Election Commission can be used for fundraising or commercial purposes. We will identify the areas (zip codes) with potential donors for future donations for similar candidates using locate_donor.py. 

Except for locations, these donations may also link to some temporal events, such as high-dollar fundraising dinners. So we will also look for time pattern of donations, so that an analyst might later correlate them to specific fundraising events.

# Summary

This script will take "contributions by individuals" data published on http://classic.fec.gov/finance/disclosure/ftpdet.shtml, extract the time, location, donation amount and recipient ID information and generate two output files.

1. `medianvals_by_zip.txt`: contains a calculated running median, total dollar amount and total number of contributions by recipient and zip code.
Each line of this file should contain these fields:
* recipient of the contribution. 
* 5-digit zip code of the contributor. 
* running median of contributions received by recipient from the contributor's zip code streamed in so far.
* total number of transactions received by recipient from the contributor's zip code streamed in so far.
* total amount of contributions received by recipient from the contributor's zip code streamed in so far.

2. `medianvals_by_date.txt`: contains the calculated median, total dollar amount and total number of contributions by recipient and date.
Each line of this file should contain these fields:
* recipeint of the contribution.
* date of the contribution.
* median of contributions received by recipient on that date.
* total number of transactions received by recipient on that date.
* total amount of contributions received by recipient on that date.

# Dependencies and Run instructions

Only tested on python 2.7. Packages required: sys, os, datetime, numpy.

This script checks existence of output files to avoid overwrite. Please remove previous outputs or change their names before run this script.

## Test details(Optional)

1. small scale test file, test if script gives median or mean.

2. this test file tests check_format function. The 2th line in the input file is not in the standard FEC format. The script should stop here.

3. this test file tests check_line function. The first three transactions has non-empty OTHER_ID, malformated donation amount and missing recipient ID respectively. These transactions should be skipped by both output files.

4. this test file tests check_line_zip function. The 2nd transaction zip code is 4-digit long, invalid. This transaction should be skipped in zip code file, medianvals_by_zip.txt. But this transaction should be kept in date file, medianvals_by_date.txt.

5. this test file tests check_line_date function. The first three transaction date are malformed, invalid. These transactions should be skipped by date file, medianvals_by_date.txt. But these transactions should be kept in zip file, medianvals_by_zip.txt.

6. this test file tests update_zipDic function. The 1st and 2nd transactions were from the same zip code. And the 3rd and 4th transactions were from another zip code. medianvals_by_zip.txt should show the real-time update and merge of donations from one zip code.

7. this test file tests update_dtDic function. The 1st and 5th transactions to the same recipient on the same day. They should be joined in medianvals_by_date.txt. The 1st, 5th and 2nd transactions were to the same recipient but at two dates. They should be sorted by time in medianvals_by_date.txt. The 3rd and 4th transactions were to a differnt recipient at two days. They should be sorted by IDs first, which separate them from the first recipient and then sorted by time. The two dates are 12312016 and 08312017, which tests tests that the donations are sorted by time not number.




