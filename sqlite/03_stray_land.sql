-- 출처를 알 수 없는 신규생성 지번의
-- 부번은 모두 0이 아님
WITH stray_land AS(
SELECT DISTINCT
조서구분,
'2022' AS 생년,
소재2022 AS 소재,
대장구분,
본번2022 AS 본번,
부번2022 AS 부번
FROM godeok
WHERE
소재2022 IS NOT NULL AND
소재2021 IS NULL AND
(조서구분 IS NULL OR
조서구분 <> '2')
UNION
SELECT DISTINCT
조서구분,
'2021' AS 생년,
소재2021 AS 소재,
대장구분,
본번2021 AS 본번,
부번2021 AS 부번
FROM godeok
WHERE
소재2021 IS NOT NULL AND
소재2020 IS NULL
UNION
SELECT DISTINCT
조서구분,
'2020' AS 생년,
소재2020 AS 소재,
대장구분,
본번2020 AS 본번,
부번2020 AS 부번
FROM godeok
WHERE
소재2020 IS NOT NULL AND
소재2019 IS NULL
UNION
SELECT DISTINCT
조서구분,
'2019' AS 생년,
소재2019 AS 소재,
대장구분,
본번2019 AS 본번,
부번2019 AS 부번
FROM godeok
WHERE
소재2019 IS NOT NULL AND
소재2018 IS NULL AND
(조서구분 IS NULL OR
조서구분 <> '1')
UNION
SELECT DISTINCT
조서구분,
'2018' AS 생년,
소재2018 AS 소재,
대장구분,
본번2018 AS 본번,
부번2018 AS 부번
FROM godeok
WHERE
소재2018 IS NOT NULL AND
소재2017 IS NULL
UNION
SELECT DISTINCT
조서구분,
'2017' AS 생년,
소재2017 AS 소재,
대장구분,
본번2017 AS 본번,
부번2017 AS 부번
FROM godeok
WHERE
소재2017 IS NOT NULL AND
소재2016 IS NULL AND
(조서구분 IS NULL OR
조서구분 <> '0')
UNION
SELECT DISTINCT
조서구분,
'2016' AS 생년,
소재2016 AS 소재,
대장구분,
본번2016 AS 본번,
부번2016 AS 부번
FROM godeok
WHERE
소재2016 IS NOT NULL AND
소재2015 IS NULL
UNION
SELECT DISTINCT
조서구분,
'2015' AS 생년,
소재2015 AS 소재,
대장구분,
본번2015 AS 본번,
부번2015 AS 부번
FROM godeok
WHERE
소재2015 IS NOT NULL AND
소재2014 IS NULL)
SELECT 조서구분, 생년, 소재, 법정동코드, 대장구분, 본번, 부번
FROM stray_land
LEFT JOIN code
ON 소재=법정동이름;
