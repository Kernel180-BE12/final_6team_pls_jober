-- V1__alter_category_table.sql
SET @col := (
  SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
  WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'category'
    AND COLUMN_NAME = 'is_active'
);

SET @sql := IF(@col = 0,
  'ALTER TABLE category ADD COLUMN is_active TINYINT(1) NOT NULL DEFAULT 1 AFTER name;',
  'SELECT 1'
);

PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
