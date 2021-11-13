type => StarID::SearchCat
fields => ID,RA,DEC,MAGB1,MAGR1,MAGB2,MAGR2,MAGN,PM,NI,SG,DIST
data => USNOB1
catalog/type => Indexed
catalog/n => 4

subtype => ub1
sort => m3
envvar => UB1_PATH
# USNO B1 server from Harvard:
data => USNOB1
location => http://tdc-www.harvard.edu/cgi-bin/scat
limit => 10000
