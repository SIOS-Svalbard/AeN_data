--CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
INSERT INTO aen(
  eventid, 
  parenteventid, 
  cruisenumber,
  cruisename, 
  stationname, 
  eventtime, 
  eventdate, 
  decimallongitude, 
  sampletype, 
  decimallatitude, 
  geartype, 
  sampledepthinmeters, 
  bottomdepthinmeters, 
  bottlenumber, 
  samplingprotocol, 
  samplelocation, 
  pi_name, 
  pi_email, 
  pi_institution, 
  recordedby, 
  eventremarks, 
  other, 
  metadata, 
  created, 
  modified, 
  history, 
  source
  )
  SELECT 
  uuid_generate_v1(), 
  parenteventid, 
  cruisenumber,
  cruisename 
  stationname, 
  eventtime, 
  eventdate, 
  decimallongitude, 
  sampletype, 
  decimallatitude, 
  'Topas40', 
  sampledepthinmeters, 
  bottomdepthinmeters, 
  bottlenumber, 
  samplingprotocol, 
  samplelocation, 
  pi_name, 
  pi_email, 
  pi_institution, 
  'Luke Marsden', 
  eventremarks, 
  other, 
  metadata, 
  now(), 
  now(), 
  TO_CHAR(now() 
	at time zone 'utc','YYYY-MM-DD"T"HH24:MI:SS"Z"') 
		|| ': New sample used to split gear type in two from Topas40, SBP300' , 
  'Manual input'
FROM 
  aen
  WHERE geartype like 'Topas40, SBP300';
