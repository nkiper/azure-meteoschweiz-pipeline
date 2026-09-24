EXEC sp_rename '[ogd-smn_d_recent]', 'legacy_ogd-smn_d_recent';

SELECT name FROM sys.tables WHERE name LIKE '%ogd-smn_d_recent%';