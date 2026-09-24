ALTER TABLE [lf-ogd-smn_d_recent] ADD date_id INT;
GO

UPDATE fact
SET fact.date_id = dim.date_id
FROM [lf-ogd-smn_d_recent] fact
JOIN [dim_date] dim ON CAST(fact.reference_timestamp AS DATE) = CAST(dim.full_date AS DATE);

SELECT COUNT(*) FROM [lf-ogd-smn_d_recent] WHERE date_id IS NULL;

ALTER TABLE [lf-ogd-smn_d_recent] ALTER COLUMN date_id INT NOT NULL;

ALTER TABLE [lf-ogd-smn_d_recent]
ADD CONSTRAINT FK_lf_date FOREIGN KEY (date_id) REFERENCES [dim_date](date_id);

SELECT name FROM sys.foreign_keys WHERE parent_object_id = OBJECT_ID('lf-ogd-smn_d_recent');

SELECT COUNT(*) FROM [lf-ogd-smn_d_recent] WHERE station_id IS NULL OR parameter_id IS NULL;