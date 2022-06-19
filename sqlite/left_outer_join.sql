/*
-- 단 1개뿐인 토지
SELECT * FROM godeok
WHERE 소재2015 IS NULL
AND 소재2021 IS NULL
AND 소재2022 IS NULL;
*/
-- 2021년에도 살아"남아서" 2021년 도형만 있는 지번
-- EXPLAIN QUERY PLAN
WITH godeok_tmp AS
(SELECT DISTINCT
법정동코드||대장구분||본번2015||부번2015 AS land_code,
조서구분
FROM godeok
LEFT JOIN code
ON 소재2015=법정동이름
WHERE 소재2021 IS NULL AND 소재2015 IS NOT NULL)
SELECT godeok_tmp.*
FROM godeok_tmp
LEFT JOIN map
ON map.land_code=godeok_tmp.land_code
WHERE map.year='2021';
