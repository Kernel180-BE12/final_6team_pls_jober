-- 카테고리 사용량 추적 및 생성자 정보 추가
-- usage_count 컬럼 추가
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
     WHERE TABLE_SCHEMA = DATABASE() 
     AND TABLE_NAME = 'category' 
     AND COLUMN_NAME = 'usage_count') = 0,
    'ALTER TABLE category ADD COLUMN usage_count INT NOT NULL DEFAULT 0 AFTER is_active',
    'SELECT "Column usage_count already exists" as message'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- created_by 컬럼 추가
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
     WHERE TABLE_SCHEMA = DATABASE() 
     AND TABLE_NAME = 'category' 
     AND COLUMN_NAME = 'created_by') = 0,
    'ALTER TABLE category ADD COLUMN created_by VARCHAR(20) NOT NULL DEFAULT "AI" AFTER usage_count',
    'SELECT "Column created_by already exists" as message'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- created_at 컬럼 추가
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
     WHERE TABLE_SCHEMA = DATABASE() 
     AND TABLE_NAME = 'category' 
     AND COLUMN_NAME = 'created_at') = 0,
    'ALTER TABLE category ADD COLUMN created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP AFTER created_by',
    'SELECT "Column created_at already exists" as message'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;


-- 기존 데이터의 created_by를 'MANAGER'로 설정 (시드 데이터)
UPDATE category SET created_by = 'MANAGER' WHERE created_by = 'AI';
