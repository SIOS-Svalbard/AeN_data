COPY (SELECT REGEXP_REPLACE(ROW_TO_JSON(t)::TEXT,'\\\\','\\','g')
FROM (SELECT * FROM aen) t)
TO 

