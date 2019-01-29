create or replace function
change_hstore_key(h hstore, from_key text, to_key text) returns hstore as $$
begin
    if h ? from_key then
        return (h - from_key) || hstore(to_key, h -> from_key);
    end if;
    return h;
end
$$ language plpgsql;

update aen set other=change_hstore_key(other, 'seaWaterSalinity', 'seaWaterElectricalConductivity') where geartype LIKE '%CTD%' and exist(other, 'seaWaterSalinity') ;
