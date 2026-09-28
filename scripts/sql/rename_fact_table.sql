EXEC sp_rename '[lf-ogd-smn_d_recent]', 'lf-ogd-smn_d';

SELECT name FROM sys.tables WHERE name LIKE '%lf-ogd-smn%';