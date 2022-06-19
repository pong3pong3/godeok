-- 2017년에 사라진 줄로만 알았던 주소가 2015년 불쑥
WITH past AS(
    SELECT 대장구분, 소재2015, 본번2015, 부번2015
    FROM godeok
    WHERE 소재2015 IS NOT NULL
    AND 소재2016 IS NULL)
SELECT past.*, 소재2021, 본번2021, 부번2021
FROM godeok AS future
INNER JOIN past
ON future.대장구분=past.대장구분
AND 소재2018=past.소재2015
AND 본번2018=past.본번2015
AND 부번2018=past.부번2015
WHERE 소재2018 IS NOT NULL
AND 소재2017 IS NULL;
-- before_20151118 주소제거
DELETE FROM godeok
WHERE 소재2015 IS NOT NULL
AND 소재2016 IS NULL
AND 등록전환구분 IS NULL;
-- 사라진 것으로 처리된 주소 채워주기
UPDATE godeok
SET
소재2017=소재2018,
본번2017=본번2018,
부번2017=부번2018,
소재2016=소재2018,
본번2016=본번2018,
부번2016=부번2018,
소재2015=소재2018,
본번2015=본번2018,
부번2015=부번2018,
소재2014=소재2018,
본번2014=본번2018,
부번2014=부번2018
WHERE 소재2018='고덕면 궁리'
AND 대장구분='1'
AND 본번2018='0325'
AND 부번2018='0004';
