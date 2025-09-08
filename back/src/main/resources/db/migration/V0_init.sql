-- ─── 사용자 계정 (Account) ───────────────────────
CREATE TABLE account (
                         account_id    BIGINT PRIMARY KEY AUTO_INCREMENT,
                         user_name     VARCHAR(50)   NOT NULL,
                         email         VARCHAR(255)  NOT NULL,
                         password_hash VARCHAR(255)  NOT NULL,
                         phone_number  VARCHAR(20),
                         role          VARCHAR(20)   NOT NULL,
                         status        VARCHAR(20)   NOT NULL,
                         company_name  VARCHAR(100),                    -- 회사 이름
                         biz_reg_no    VARCHAR(12),                     -- 사업자등록번호
                         created_at    TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
                         updated_at    TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) DEFAULT CHARSET = utf8mb4;


-- ─── 카테고리 1 ───────────────────────────────
-- 대분류 카테고리 정보
CREATE TABLE category1 (
                           category1_id BIGINT PRIMARY KEY AUTO_INCREMENT,
                           name         VARCHAR(100) NOT NULL
)DEFAULT CHARSET=utf8mb4;


-- ─── 카테고리 2 ───────────────────────────────
-- 소분류 카테고리 정보, category1과 연결
CREATE TABLE category2 (
                           category2_id BIGINT PRIMARY KEY AUTO_INCREMENT,
                           category1_id BIGINT NOT NULL,
                           name         VARCHAR(100) NOT NULL,
                           CONSTRAINT fk_category2_category1 FOREIGN KEY (category1_id)
                               REFERENCES category1(category1_id)
)DEFAULT CHARSET=utf8mb4;


-- ─── 버튼 ───────────────────────────────
-- url은 인덱싱/제약 고려해 VARCHAR(1000) 권장
-- TEXT는 인덱스/제약이 까다로움
CREATE TABLE button (
                        button_id   BIGINT PRIMARY KEY AUTO_INCREMENT,
                        url         VARCHAR(1000) NOT NULL,
                        button_text VARCHAR(100)  NOT NULL
)DEFAULT CHARSET=utf8mb4;


-- ─── 업종 ───────────────────────────────
CREATE TABLE industry (
                          industry_id   BIGINT PRIMARY KEY AUTO_INCREMENT,
                          industry_name VARCHAR(50) NOT NULL
) DEFAULT CHARSET = utf8mb4;


-- ─── 알림톡 템플릿 ─────────────────────
CREATE TABLE template (
                          template_id      BIGINT PRIMARY KEY AUTO_INCREMENT,
                          account_id       BIGINT NOT NULL,
                          category2_id     BIGINT,
                          button_id        BIGINT,
                          industry_id      BIGINT,
                          template_content VARCHAR(1000) NOT NULL,
                          auto_title       VARCHAR(255),
                          image_url        VARCHAR(255),
                          created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                          template_addon   VARCHAR(1000),
                          status           VARCHAR(20),

                          CONSTRAINT fk_template_account
                              FOREIGN KEY (account_id)   REFERENCES account(account_id),
                          CONSTRAINT fk_template_category2
                              FOREIGN KEY (category2_id) REFERENCES category2(category2_id),
                          CONSTRAINT fk_template_button
                              FOREIGN KEY (button_id)    REFERENCES button(button_id),
                          CONSTRAINT fk_template_industry
                              FOREIGN KEY (industry_id)  REFERENCES industry(industry_id)
) DEFAULT CHARSET = utf8mb4;


-- 변수 (var) ───────────────────────────────
CREATE TABLE var (
                     variable_id    BIGINT PRIMARY KEY AUTO_INCREMENT,
                     template_id    BIGINT NOT NULL,
                     variable_key   VARCHAR(100) NOT NULL,
                     variable_value VARCHAR(1000),
                     variable_type  VARCHAR(100),
                     CONSTRAINT fk_var_template
                         FOREIGN KEY (template_id) REFERENCES template(template_id)
) DEFAULT CHARSET = utf8mb4;