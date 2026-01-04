CREATE OR REPLACE DATABASE STOCKGUARD_DB;
USE DATABASE STOCKGUARD_DB;

CREATE OR REPLACE SCHEMA PUBLIC;
USE SCHEMA PUBLIC;

CREATE OR REPLACE TABLE USERS (
    username STRING,
    password STRING,
    role STRING,
    org_type STRING,
    created_at TIMESTAMP
);

CREATE OR REPLACE TABLE BASIC (
    mfd DATE,
    exd DATE,
    location_id STRING,
    item_id STRING,
    opening_stock INT,
    received INT,
    issued INT,
    closing_stock INT,
    lead_time_days INT
);
