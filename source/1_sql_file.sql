UPDATE dfn_ntp.v00_sys_config v00
	SET v00.v00_value = '10.043.3.0',
		v00.v00_description = 'DFNNTP-DB_SA_ALKB_10.043.3.0',
		v00_status_changed_date = SYSDATE, v00_modified_date = SYSDATE
	WHERE v00.v00_key = 'VER_DB';

INSERT INTO dfn_ntp.z10_version_audit_log
	VALUES(dfn_ntp.seq_z10_ver_audit_log.NEXTVAL,
			'DB Patch',
			SYSDATE,
			'DFNNTP-DB_X_X_10.009.89.0',
			'DFNNTP-DB_SA_X_10.066.0.0',
			'DFNNTP-DB_SA_ALKB_10.043.3.0');

DECLARE
    l_count   NUMBER := 0;
    l_ddl     VARCHAR2 (1000)
        := 'ALTER TABLE dfn_ntp.U09_CUSTOMER_LOGIN  ADD (  U09_LAST_RESENT_TIME TIMESTAMP (6) DEFAULT SYSTIMESTAMP )';
BEGIN
    SELECT COUNT (*)
      INTO l_count
      FROM all_tab_columns
     WHERE     owner = UPPER ('dfn_ntp')
           AND table_name = UPPER ('u09_customer_login')
           AND column_name = UPPER ('u09_last_resent_time');
    IF l_count = 0
    THEN
        EXECUTE IMMEDIATE l_ddl;
    END IF;
END;
/

INSERT INTO dfn_ntp.z02_forms_cols (Z02_Z01_ID,Z02_MAPPING_NAME,Z02_COLUMN_NAME,Z02_WIDTH,Z02_ALIGNMENT,Z02_FORMAT,Z02_SEQ_NO,Z02_VISIBLE,Z02_TRANSLATABLE,Z02_SHOW_BY_DEFAULT,Z02_FORCE_DEFAULT_FORMATTING,Z02_ADJUST_GMT,Z02_FORMAT_BASED_ON_CURRENCY,Z02_CURRENCY_FIELD_NAME,Z02_SHOW_TOTAL,Z02_FIXED_FILTER_VALUE,Z02_MIN_FILTER_LENGTH,Z02_SHOW_IN_FILTER,Z02_COLUMN_TYPE,Z02_FEATURE_ID_V14,Z02_CASE_SENSITIVE,Z02_OPERATOR)
VALUES(384,'v04Id','Id',120,1,NULL,1,1,0,1,0,0,0,NULL,0,NULL,0,1,1,NULL,0,1);
INSERT INTO dfn_ntp.z02_forms_cols (Z02_Z01_ID,Z02_MAPPING_NAME,Z02_COLUMN_NAME,Z02_WIDTH,Z02_ALIGNMENT,Z02_FORMAT,Z02_SEQ_NO,Z02_VISIBLE,Z02_TRANSLATABLE,Z02_SHOW_BY_DEFAULT,Z02_FORCE_DEFAULT_FORMATTING,Z02_ADJUST_GMT,Z02_FORMAT_BASED_ON_CURRENCY,Z02_CURRENCY_FIELD_NAME,Z02_SHOW_TOTAL,Z02_FIXED_FILTER_VALUE,Z02_MIN_FILTER_LENGTH,Z02_SHOW_IN_FILTER,Z02_COLUMN_TYPE,Z02_FEATURE_ID_V14,Z02_CASE_SENSITIVE,Z02_OPERATOR)
VALUES(384,'v04TaskName','Task Name',120,1,NULL,2,1,0,1,0,0,0,NULL,0,NULL,0,1,1,NULL,0,1);

MERGE INTO dfn_ntp.v00_sys_config
 USING DUAL
    ON (v00_key = 'OTP_RESEND_DELAY_PERIOD')
WHEN NOT MATCHED
THEN
    INSERT (v00_id,
            v00_value,
            v00_description,
            v00_key,
            v00_status_id_v01,
            v00_status_changed_by_id_u17,
            v00_status_changed_date,
            v00_modified_by_id_u17,
            v00_modified_date,
            v00_type,
            v00_custom_type,
            v00_is_root_parameter)
    VALUES (fn_get_next_sequnce ('V00_SYS_CONFIG'),
            '30000',
            'OTP generate delay time period in milliseconds',
            'OTP_RESEND_DELAY_PERIOD',
            2,
            NULL,
            SYSDATE,
            NULL,
            SYSDATE,
            1,
            '1',
            0);
COMMIT;

UPDATE dfn_ntp.z02_forms_cols
   SET z02_format = '1.2-2'
 WHERE z02_z01_id = 179 AND z02_mapping_name = 'currentMarginPercentage';

COMMIT;