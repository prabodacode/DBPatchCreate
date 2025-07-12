-- [#BASE_VERSION] VERSION END --

-- [#PATCH_VERSION] VERSION UPDATE START --
BEGIN
	UPDATE dfn_ntp.v00_sys_config v00
		SET v00.v00_value = '[#PATCH_VERSION_NUMBERS]',
			v00.v00_description = '[#PATCH_VERSION]',
			v00_status_changed_date = SYSDATE, v00_modified_date = SYSDATE 
		WHERE v00.v00_key = 'VER_DB';

	INSERT INTO dfn_ntp.z10_version_audit_log
		VALUES(dfn_ntp.seq_z10_ver_audit_log.NEXTVAL,
				'DB Patch',
				SYSDATE,
				'[#CORE_VERSION]',
				'[#COUNTRY_VERSION]',
				'[#PATCH_VERSION]');
END;
/

COMMIT; 

-- [#PATCH_VERSION] VERSION UPDATE END --