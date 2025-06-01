
CREATE TABLE dfn_ntp.a06_audit
(
    a06_id                  NUMBER (38, 0),
    a06_date                DATE DEFAULT SYSDATE,
    a06_user_id_u17         NUMBER (10, 0),
    a06_activity_id_m82     NUMBER (7, 0),
    a06_description         VARCHAR2 (2000),
    a06_reference_no        VARCHAR2 (400),
    a06_channel_v29         NUMBER (3, 0),
    a06_customer_id_u01     NUMBER (18, 0),
    a06_login_id_u09        NUMBER (20, 0),
    a06_user_login_id_u17   NUMBER (20, 0),
    a06_ip                  VARCHAR2 (100),
    a06_connected_machine   VARCHAR2 (100)
)
/

INSERT INTO dfn_ntp.z02_forms_cols (Z02_Z01_ID,Z02_MAPPING_NAME,Z02_COLUMN_NAME,Z02_WIDTH,Z02_ALIGNMENT,Z02_FORMAT,Z02_SEQ_NO,Z02_VISIBLE,Z02_TRANSLATABLE,Z02_SHOW_BY_DEFAULT,Z02_FORCE_DEFAULT_FORMATTING,Z02_ADJUST_GMT,Z02_FORMAT_BASED_ON_CURRENCY,Z02_CURRENCY_FIELD_NAME,Z02_SHOW_TOTAL,Z02_FIXED_FILTER_VALUE,Z02_MIN_FILTER_LENGTH,Z02_SHOW_IN_FILTER,Z02_COLUMN_TYPE,Z02_FEATURE_ID_V14,Z02_CASE_SENSITIVE,Z02_OPERATOR)
VALUES(384,'v04TaskName','Task Name',120,1,NULL,2,1,0,1,0,0,0,NULL,0,NULL,0,1,1,NULL,0,1);

CREATE OR REPLACE PROCEDURE get_forms_menu (
    updated_datetime   IN     VARCHAR2,
    p_view                OUT SYS_REFCURSOR,
    prows                 OUT NUMBER)
IS
BEGIN
    OPEN p_view FOR
        SELECT *
          FROM vw_z03_forms_menu
         WHERE UPPER (z03_z01_id) IN
                   (SELECT z01_id
                      FROM z01_forms_m
                     WHERE z01_menus_updated_datetime >
                               TO_DATE (updated_datetime,
                                        'dd/MM/yyyy hh24:mi:ss'))
        ORDER BY z03_z01_id;
END;
/

MERGE INTO dfn_ntp.m148_notify_events_master
     USING DUAL
        ON (m148_id = 205)
WHEN NOT MATCHED
THEN
    INSERT     (m148_id,
                m148_event_cat_id_m145,
                m148_description,
                m148_description_lang,
                m148_key_field1,
                m148_key_field2,
                m148_key_field3,
                m148_id_m100,
                m148_key_field4,
                m148_key_field5,
                m148_key_field6)
        VALUES (205,
                4,
                'Derivative Buy to Close (Filled)',
                'Derivative Buy to Close (Filled)',
                '1',
                'FUT',
                '2',
                2,
                '1',
                'C',
                NULL);
COMMIT;
