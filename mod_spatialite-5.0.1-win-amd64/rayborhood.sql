SELECT load_extension('mod_spatialite');
/*
ALTER TABLE ray
ADD spatiotemporal_class INTEGER;

--very correlated subquery
EXPLAIN
    WITH
    classes AS (
    SELECT
        ROW_NUMBER() OVER (ORDER BY COUNT(fid) DESC) AS spatiotemporal_class,
        IFNULL(village_code_2020,'') AS village_code_2020,
        IFNULL(village_code_2019,'') AS village_code_2019,
        IFNULL(register_order,'') AS register_order,
        IFNULL(cancellation_order,'') AS cancellation_order
    FROM ray
    GROUP BY
        village_code_2020,
        village_code_2019,
        register_order,
        cancellation_order)
    UPDATE ray
    SET spatiotemporal_class = (
        SELECT classes.spatiotemporal_class
        FROM classes
        WHERE
            IFNULL(ray.village_code_2020,'')=classes.village_code_2020 AND
            IFNULL(ray.village_code_2019,'')=classes.village_code_2019 AND
            IFNULL(ray.register_order,'')=classes.register_order AND
            IFNULL(ray.cancellation_order,'')=classes.cancellation_order
            );

--temporary table
CREATE TEMPORARY TABLE
classes AS
     SELECT
        ROW_NUMBER() OVER (ORDER BY COUNT(fid) DESC) AS spatiotemporal_class,
        IFNULL(village_code_2022,'') AS village_code_2022,
        IFNULL(village_code_2021,'') AS village_code_2021,
        IFNULL(village_code_2020,'') AS village_code_2020,
        IFNULL(village_code_2019,'') AS village_code_2019,
        IFNULL(village_code_2018,'') AS village_code_2018,
        IFNULL(village_code_2017,'') AS village_code_2017,
        IFNULL(village_code_2016,'') AS village_code_2016,
        IFNULL(register_order,'') AS register_order,
        IFNULL(cancellation_order,'') AS cancellation_order
    FROM ray
    GROUP BY
        village_code_2022,
        village_code_2021,
        village_code_2020,
        village_code_2019,
        village_code_2018,
        village_code_2017,
        village_code_2016,
        register_order,
        cancellation_order;

UPDATE ray
SET spatiotemporal_class = (
    SELECT classes.spatiotemporal_class
    FROM classes
    WHERE
        IFNULL(ray.village_code_2022,'')=classes.village_code_2022 AND
        IFNULL(ray.village_code_2021,'')=classes.village_code_2021 AND
        IFNULL(ray.village_code_2020,'')=classes.village_code_2020 AND
        IFNULL(ray.village_code_2019,'')=classes.village_code_2019 AND
        IFNULL(ray.village_code_2018,'')=classes.village_code_2018 AND
        IFNULL(ray.village_code_2017,'')=classes.village_code_2017 AND
        IFNULL(ray.village_code_2016,'')=classes.village_code_2016 AND
        IFNULL(ray.register_order,'')=classes.register_order AND
        IFNULL(ray.cancellation_order,'')=classes.cancellation_order
        );

*/
-- dissolve
SELECT EnableGpkgMode();

DELETE FROM gpkg_geometry_columns
WHERE table_name='rayborhood';
DROP TABLE IF EXISTS rayborhood;
CREATE TABLE rayborhood
(village_name_2022 TEXT,
village_name_2021 TEXT,
village_name_2020 TEXT,
village_name_2019 TEXT,
village_name_2018 TEXT,
village_name_2017 TEXT,
village_name_2016 TEXT);

SELECT gpkgAddGeometryColumn(
	'rayborhood','geom','Geometry',0,0,5174);

INSERT INTO rayborhood
SELECT
a.village_name AS village_name_2022,
b.village_name AS village_name_2021, 
c.village_name AS village_name_2020,
d.village_name AS village_name_2019,
e.village_name AS village_name_2018,
f.village_name AS village_name_2017,
g.village_name AS village_name_2016,
ST_Union(geom) AS geom
FROM ray
LEFT JOIN village_code_table AS a
ON a.village_code=village_code_2022
LEFT JOIN village_code_table AS b
ON b.village_code=village_code_2021
LEFT JOIN village_code_table AS c
ON c.village_code=village_code_2020
LEFT JOIN village_code_table AS d
ON d.village_code=village_code_2019
LEFT JOIN village_code_table AS e
ON e.village_code=village_code_2018
LEFT JOIN village_code_table AS f
ON f.village_code=village_code_2017
LEFT JOIN village_code_table AS g
ON g.village_code=village_code_2016
WHERE geom IS NOT NULL
GROUP BY
village_code_2022,
village_code_2021,
village_code_2020,
village_code_2019,
village_code_2018,
village_code_2017,
village_code_2016
ORDER BY COUNT(fid) DESC;
