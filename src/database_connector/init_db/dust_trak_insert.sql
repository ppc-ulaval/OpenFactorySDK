USE mytest;
GO

INSERT INTO EquipmentType (Nom, Description)
VALUES 
('Photometer', 'Device for measuring light intensity.');

INSERT INTO Manufacturer (Nom, Description)
VALUES 
('TSI', 'TSI Incorporated is a global leader in measurement solutions, providing innovative instruments for various industries.');

INSERT INTO Model (Nom, Description)
VALUES 
('Test', 'Test');

INSERT INTO Type (Nom, Description)
VALUES 
('Concentration', 'The measurement of the percentage of one component within a mixture of components. ');


DECLARE @Type INT = (SELECT Id FROM EquipmentType WHERE Nom = 'Photometer');
DECLARE @Mfr INT = (SELECT Id FROM Manufacturer WHERE Nom = 'TSI');
DECLARE @Model INT = (SELECT Id FROM Model WHERE Nom = 'Test');

INSERT INTO Equipment (Id, ParentEquipmentId, EquipmentTypeId, ManufacturerId, ModelId, RoomId, Nom, PrefabKey, SerialNumber, PurchaseDate)
VALUES 
('11', NULL, @Type, @Mfr, @Model, 'room-001', 'DustTrak Environmental Monitor', 'DustTrak_Prefab', '8543210412', '2025-08-01');

DECLARE @TypeConcentration INT = (SELECT Id FROM Type WHERE Nom = 'Concentration');
DECLARE @TypePosition INT = (SELECT Id FROM Type WHERE Nom = 'Position');
DECLARE @TypeAngle INT = (SELECT Id FROM Type WHERE Nom = 'Angle');

INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('pm1_concentration', @TypeConcentration, '11');
DECLARE @VarPM1 INT = SCOPE_IDENTITY();

INSERT INTO OpenFactoryLink (VariableId, AssetUuid, DataItemId)
VALUES (@VarPM1, 'DUSTTRAK', 'pm1_concentration');

INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('pm2_5_concentration', @TypeConcentration, '11');
DECLARE @VarPM2_5 INT = SCOPE_IDENTITY();

INSERT INTO OpenFactoryLink (VariableId, AssetUuid, DataItemId)
VALUES (@VarPM2_5, 'DUSTTRAK', 'pm2_5_concentration');

INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('pm4_concentration', @TypeConcentration, '11');
DECLARE @VarPM4 INT = SCOPE_IDENTITY();

INSERT INTO OpenFactoryLink (VariableId, AssetUuid, DataItemId)
VALUES (@VarPM4, 'DUSTTRAK', 'pm4_concentration');

INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('pm10_concentration', @TypeConcentration, '11');
DECLARE @VarPM10 INT = SCOPE_IDENTITY();

INSERT INTO OpenFactoryLink (VariableId, AssetUuid, DataItemId)
VALUES (@VarPM10, 'DUSTTRAK', 'pm10_concentration');

INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('PositionX', @TypePosition, '11');
DECLARE @VarPosX INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value, Timestamp)
VALUES (@VarPosX, 4.5, CURRENT_TIMESTAMP);

INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('PositionY', @TypePosition, '11');
DECLARE @VarPosY INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value, Timestamp)
VALUES (@VarPosY, 0.0, CURRENT_TIMESTAMP);

INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('PositionZ', @TypePosition, '11');
DECLARE @VarPosZ INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value, Timestamp)
VALUES (@VarPosZ, 1.2, CURRENT_TIMESTAMP);

INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('AngleX', @TypeAngle, '11');
DECLARE @VarAngleX INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value, Timestamp)
VALUES (@VarAngleX, 0.0, CURRENT_TIMESTAMP);

INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('AngleY', @TypeAngle, '11');
DECLARE @VarAngleY INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value, Timestamp)
VALUES (@VarAngleY, 0.0, CURRENT_TIMESTAMP);

INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('AngleZ', @TypeAngle, '11');
DECLARE @VarAngleZ INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value, Timestamp)
VALUES (@VarAngleZ, 0.0, CURRENT_TIMESTAMP);