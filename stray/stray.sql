-- 혹시나 2019-298호 가운데 실종지들이 2017-427호 사망지에?!
WITH ancient AS(
    SELECT 
    village_code_2016,
    ledger_code,
    land_main_code_2016,
    land_sub_code_2016
    FROM ray
    WHERE cancellation_order='0')
SELECT
village_code_2018,
ledger_code,
land_main_code_2018,
land_sub_code_2018
FROM ray AS medieval
WHERE cancellation_order IS NULL
AND village_code_2018 IS NOT NULL
AND village_code_2019 IS NULL
AND EXISTS (
    SELECT * FROM ancient
    WHERE village_code_2016=village_code_2018
    AND ancient.ledger_code=medieval.ledger_code
    AND land_main_code_2016=land_main_code_2018
    AND land_sub_code_2016=land_sub_code_2018);

-- 아님 혹시 2019-2393호의 사생지와 관련?!
SELECT
village_name,
CASE WHEN ledger_code='1' THEN ''
ELSE '산' END AS ledger,
CAST(land_main_code_2019 AS INT) AS main,
CAST(land_sub_code_2019 AS INT) AS sub
FROM ray
LEFT JOIN village_code_table
ON village_code_2019=village_code
WHERE register_order IS NULL
AND village_name='고덕면 여염리'
AND village_code_2018 IS NULL;

-- 2015년 지적도랑 실종지 대조
.once stray.txt

SELECT
village_code_2018 || ledger_code || land_main_code_2018 || land_sub_code_2018
AS pnu
FROM ray
WHERE cancellation_order IS NULL
AND village_code_2018 IS NOT NULL
AND village_code_2019 IS NULL
UNION
SELECT
village_code_2017 || ledger_code || land_main_code_2017 || land_sub_code_2017
AS pnu
FROM ray
WHERE cancellation_order IS NULL
AND village_code_2018 IS NOT NULL
AND village_code_2019 IS NULL
ORDER BY pnu
