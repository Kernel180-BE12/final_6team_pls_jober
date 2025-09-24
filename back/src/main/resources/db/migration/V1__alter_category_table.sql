-- 카테고리 테이블 신규 컬럼 추가
ALTER TABLE category
    ADD COLUMN is_active TINYINT(1) NOT NULL DEFAULT 1 AFTER name;
