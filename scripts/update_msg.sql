update aen set 
-- 	sampletype='Methylmercury',
	geartype = 'GO-FLO',
--	other = other ||'"intendedMethod"=>"Microscopy"',
--	other = other ||'"tissueType"=>"Isotope (muscle tissue)"',
--	other = other ||'"fieldNotes"=>"Pore water"',
--	other = other ||'"Taxon"=>" Ctenophore"',
--	other = other ||'"recordNumber"=>"Juveniles sieved 250um"',
--	other = other || '"minimumDepthInMeters"=>"0","maximumDepthInMeters"=>"500"',
	eventremarks = concat_ws(', ',eventremarks,'GO-flow bottle under ice'),
	modified=now(),
	history=history || E'\n'|| TO_CHAR(now() 
	at time zone 'utc','YYYY-MM-DD"T"HH24:MI:SS"Z"') 
		|| ': Changed geartype from GO-flow bottle under ice to GO-FLO and moved to remarks' 
--	from aen 
	where geartype like 'GO-flow bottle under ice';
--		and parenteventid is NULL;
--	where eventid = '39cdc332-9cf4-11e8-91c9-005056a2b019';

