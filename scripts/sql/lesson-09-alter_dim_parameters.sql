ALTER TABLE [dim_parameters] ADD corr_m_id INT NULL, corr_d_id INT NULL;

SELECT COLUMN_NAME FROM information_schema.columns WHERE table_name = 'dim_parameters';

SELECT COUNT(*) FROM [dim_parameters] WHERE corr_m_id IS NOT NULL;
SELECT COUNT(*) FROM [dim_parameters] WHERE corr_d_id IS NOT NULL;

SELECT parameter_id, corr_m_id, corr_d_id FROM [dim_parameters] WHERE parameter_shortname = 'tre200d0';
SELECT parameter_id, corr_m_id, corr_d_id FROM [dim_parameters] WHERE parameter_shortname = 'tre200m0';