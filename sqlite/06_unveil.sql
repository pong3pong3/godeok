SELECT
소재2020, 대장구분, 본번2020
FROM godeok
WHERE
소재2020 IS NOT NULL AND 소재2019 IS NULL
GROUP BY
소재2020, 대장구분, 본번2020
HAVING MIN(부번2020) <> '0001'; 

WITH left_table AS(
    SELECT DISTINCT
    소재2020, 대장구분, 본번2020, 지목 AS 새지목
    FROM godeok
    WHERE
    소재2020 IS NOT NULL AND 소재2019 IS NULL),
right_table AS(
    SELECT
    소재2020, 대장구분, 본번2020, 지목 AS 옛지목
    FROM godeok
    WHERE
    부번2020 = '0000'),
joined_table AS(
    SELECT left_table.*, 옛지목
    FROM left_table
    LEFT JOIN right_table
    ON left_table.소재2020 = right_table.소재2020
    AND left_table.대장구분 = right_table.대장구분
    AND left_table.본번2020 = right_table.본번2020)
SELECT * FROM joined_table
WHERE 옛지목 <> 새지목 OR 옛지목 IS NULL;

-- 결론: 2019년 토지를 지목변경 없이 분할하여 2020년 신규토지 생성

WITH origin AS(
    SELECT
    대장구분, 소재2020, 본번2020,
    소재2019, 본번2019, 부번2019,
    소재2018, 본번2018, 부번2018,
    소재2017, 본번2017, 부번2017,
    소재2016, 본번2016, 부번2016,
    소재2015, 본번2015, 부번2015,
    소재2014, 본번2014, 부번2014
    FROM godeok
    WHERE 부번2020='0000'),
new AS(
    SELECT
    대장구분, 소재2020, 본번2020, 부번2020
    FROM godeok
    WHERE 소재2020 IS NOT NULL
    AND 소재2019 IS NULL)
UPDATE godeok
SET
소재2019 = origin.소재2019,
본번2019 = origin.본번2019,
부번2019 = origin.부번2019,
소재2018 = origin.소재2018,
본번2018 = origin.본번2018,
부번2018 = origin.부번2018,
소재2017 = origin.소재2017,
본번2017 = origin.본번2017,
부번2017 = origin.부번2017,
소재2016 = origin.소재2016,
본번2016 = origin.본번2016,
부번2016 = origin.부번2016,
소재2015 = origin.소재2015,
본번2015 = origin.본번2015,
부번2015 = origin.부번2015,
소재2014 = origin.소재2014,
본번2014 = origin.본번2014,
부번2014 = origin.부번2014
FROM new
LEFT JOIN origin
ON new.대장구분 = origin.대장구분
AND new.소재2020 = origin.소재2020
AND new.본번2020 = origin.본번2020
WHERE godeok.대장구분 = new.대장구분
AND godeok.소재2020 = new.소재2020
AND godeok.본번2020 = new.본번2020
AND godeok.부번2020 = new.부번2020
