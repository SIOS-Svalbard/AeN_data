update aen set sampletype='Fish',
--select eventremarks,
--	other = other ||'"serialNumber"=>"3615"',
--	other = other ||'"fieldNotes"=>"Meltpond"',
	other = other ||'"Taxon"=>"Twohorn sculpin"',
--	other = other ||'"recordNumber"=>"Box core replicate 3"',
--	other = other || '"minimumDepthInMeters"=>"0","maximumDepthInMeters"=>"500"',
--	eventremarks = concat_ws(', ',eventremarks,'SUMO'),
	modified=now(), 
	history=history || E'\n'|| TO_CHAR(now() 
	at time zone 'utc','YYYY-MM-DD"T"HH24:MI:SS"Z"') 
		|| ': Moved sampletype to taxon and set sample type to Fish' 
--	from aen 
	where sampletype like 'Twohorn sculpin';
--	where eventid = '1fe58824-a2e4-11e8-91c9-005056a2b019';

