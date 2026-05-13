USE mytest;

IF OBJECT_ID('dbo.OpenFactoryLink', 'U') IS NOT NULL
    DROP TABLE dbo.OpenFactoryLink;

IF OBJECT_ID('dbo.StrValue', 'U') IS NOT NULL
    DROP TABLE dbo.StrValue;

IF OBJECT_ID('dbo.IntValue', 'U') IS NOT NULL
    DROP TABLE dbo.IntValue;

IF OBJECT_ID('dbo.FloatValue', 'U') IS NOT NULL
    DROP TABLE dbo.FloatValue;

IF OBJECT_ID('dbo.Variable', 'U') IS NOT NULL
    DROP TABLE dbo.Variable;

IF OBJECT_ID('dbo.Type', 'U') IS NOT NULL
    DROP TABLE dbo.Type;

IF OBJECT_ID('dbo.Equipment', 'U') IS NOT NULL
    DROP TABLE dbo.Equipment;

IF OBJECT_ID('dbo.EquipmentType', 'U') IS NOT NULL
    DROP TABLE dbo.EquipmentType;

IF OBJECT_ID('dbo.Manufacturer', 'U') IS NOT NULL
    DROP TABLE dbo.Manufacturer;

IF OBJECT_ID('dbo.Model', 'U') IS NOT NULL
    DROP TABLE dbo.Model;

IF OBJECT_ID('dbo.Room', 'U') IS NOT NULL
    DROP TABLE dbo.Room;

CREATE TABLE Room (
	Id NVARCHAR(255) PRIMARY KEY,
	Nom NVARCHAR(255) NOT NULL,
	Largeur FLOAT NOT NULL,
	Longueur FLOAT NOT NULL,
	Hauteur FLOAT NOT NULL,
);

CREATE TABLE EquipmentType (
	Id INT PRIMARY KEY IDENTITY,
	Nom NVARCHAR(255),
	Description Text NOT NULL
);

CREATE TABLE Manufacturer (
	Id INT PRIMARY KEY IDENTITY,
	Nom NVARCHAR(255) NOT NULL,
	Description Text NOT NULL,
);

CREATE TABLE Model (
	Id INT PRIMARY KEY IDENTITY,
	Nom NVARCHAR(255) NOT NULL,
	Description Text NOT NULL,
);

CREATE TABLE Equipment (
	Id NVARCHAR(255) PRIMARY KEY, 
	ParentEquipmentId NVARCHAR(255) FOREIGN KEY REFERENCES Equipment(Id),
	EquipmentTypeId int FOREIGN KEY REFERENCES EquipmentType(Id),
	ManufacturerId int FOREIGN KEY REFERENCES Manufacturer(Id),
	ModelId int FOREIGN KEY REFERENCES Model(Id),
	RoomId NVARCHAR(255) FOREIGN KEY REFERENCES Room(Id),
	Nom NVARCHAR(255),
	PrefabKey NVARCHAR(255),
	SerialNumber NVARCHAR(255),
	PurchaseDate Date,
);

CREATE TABLE Type (
	Id INT PRIMARY KEY IDENTITY,
	Nom NVARCHAR(255) NOT NULL,
	Description Text NOT NULL,
	Subtype NVARCHAR(255),
	Units NVARCHAR(255)
);

CREATE TABLE Variable ( 
	Id INT PRIMARY KEY IDENTITY,
	Nom NVARCHAR(255) NOT NULL,
	TypeId int FOREIGN KEY REFERENCES Type(Id),
	EquipmentId NVARCHAR(255) FOREIGN KEY REFERENCES Equipment(Id)
);

CREATE TABLE StrValue (
	Id INT PRIMARY KEY IDENTITY,
	VariableId INT FOREIGN KEY REFERENCES Variable(Id),
	Value NVARCHAR(255) NOT NULL,
	Timestamp DATETIME2 NOT NULL
);

CREATE TABLE IntValue (
	Id INT PRIMARY KEY IDENTITY,
	VariableId INT FOREIGN KEY REFERENCES Variable(Id),
	Value INT NOT NULL,
	Timestamp DATETIME2 NOT NULL
);

CREATE TABLE FloatValue (
	Id INT PRIMARY KEY IDENTITY,
	VariableId INT FOREIGN KEY REFERENCES Variable(Id),
	Value FLOAT NOT NULL,
	Timestamp DATETIME2 NOT NULL
);

CREATE TABLE OpenFactoryLink (
	DataItemId NVARCHAR(255) PRIMARY KEY,
	VariableId INT FOREIGN KEY REFERENCES Variable(Id),
	AssetUuid NVARCHAR(255) NOT NULL
)