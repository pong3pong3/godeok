SELECT
소재2018, 대장구분, 본번2018
FROM godeok
WHERE
소재2018 IS NOT NULL AND 소재2017 IS NULL
GROUP BY
소재2018, 대장구분, 본번2018
HAVING MIN(부번2018) <> '0001'; 

WITH left_table AS(
    SELECT DISTINCT
    소재2018, 대장구분, 본번2018, 지목 AS 새지목
    FROM godeok
    WHERE
    소재2018 IS NOT NULL AND 소재2017 IS NULL),
right_table AS(
    SELECT
    소재2018, 대장구분, 본번2018, 지목 AS 옛지목
    FROM godeok
    WHERE 소재2017 IS NOT NULL
    GROUP BY 소재2018, 대장구분, 본번2018
    HAVING 부번2018 = MAX(부번2018)),
joined_table AS(
    SELECT left_table.*, 옛지목
    FROM left_table
    LEFT JOIN right_table
    ON left_table.소재2018 = right_table.소재2018
    AND left_table.대장구분 = right_table.대장구분
    AND left_table.본번2018 = right_table.본번2018)
SELECT * FROM joined_table
WHERE 옛지목 <> 새지목 OR 옛지목 IS NULL;
