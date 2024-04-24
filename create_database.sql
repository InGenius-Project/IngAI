IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'ChatDatabase')
BEGIN
    CREATE DATABASE ChatDatabase;
END;

USE ChatDatabase;

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'ChatHistory' AND TABLE_SCHEMA = 'dbo')
BEGIN
    CREATE TABLE ChatHistory (
        RecordID INT PRIMARY KEY IDENTITY(1,1),
        UserID NVARCHAR(50),
        Role NVARCHAR(50),
        Content NVARCHAR(MAX),
        DateTime DATETIME DEFAULT GETDATE()
    );
END;
