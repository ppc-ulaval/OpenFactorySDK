USE mytest;
GO

INSERT INTO EquipmentType (Nom, Description)
VALUES 
('BlastGate', 'Component used in dust collection systems to control airflow by directing it to different locations.'),
('Spindle', 'Rotating axis of a CNC machine.'),
('Lathe', 'Machine tool for shaping materials.');

INSERT INTO Manufacturer (Nom, Description)
VALUES 
('Test', 'Test');

INSERT INTO Model (Nom, Description)
VALUES 
('Test', 'Test');

INSERT INTO Type (Nom, Description, SubType)
VALUES 
('EquipmentMode', 'An indication that a piece of equipment, or a subpart of a piece of equipment, is performing specific types of activities.', 'Powered');

INSERT INTO Type (Nom, Description)
VALUES 
('DoorState', 'The operational state of a DOOR type component or composition element.');

DECLARE @TypeSpindle INT = (SELECT Id FROM EquipmentType WHERE Nom = 'CNC_Spindle');
DECLARE @TypeLathe INT = (SELECT Id FROM EquipmentType WHERE Nom = 'Lathe');
DECLARE @TypeGate INT = (SELECT Id FROM EquipmentType WHERE Nom = 'BlastGate');
DECLARE @Mfr INT = (SELECT Id FROM Manufacturer WHERE Nom = 'Test');
DECLARE @Model INT = (SELECT Id FROM Model WHERE Nom = 'Test');

INSERT INTO Equipment (Id, ParentEquipmentId, EquipmentTypeId, ManufacturerId, ModelId, RoomId, Nom, PrefabKey, SerialNumber, PurchaseDate)
VALUES 
('8', NULL, @TypeLathe, @Mfr, @Model, 'room-001', 'LatheA3', 'Lathe_Prefab', 'Test', '2025-07-11'),
('9', NULL, @TypeGate, @Mfr, @Model, 'room-001', 'A2BlastGate', 'A2BlastGate_Prefab', 'Test', '2025-07-11'),
('10', NULL, @TypeGate, @Mfr, @Model, 'room-001', 'A3BlastGate', 'A3BlastGate_Prefab', 'Test', '2025-07-11');

DECLARE @TypeToolStatus INT = (SELECT Id FROM Type WHERE Nom = 'EquipmentMode');
DECLARE @TypeGateStatus INT = (SELECT Id FROM Type WHERE Nom = 'DoorState');
DECLARE @TypePosition INT = (SELECT Id FROM Type WHERE Nom = 'Position');
DECLARE @TypeAngle INT = (SELECT Id FROM Type WHERE Nom = 'Angle');

--A2ToolPlus
INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('A2ToolStatus', @TypeToolStatus, '7');
DECLARE @VarA2ToolStatus INT = SCOPE_IDENTITY();

INSERT INTO StrValue (VariableId, Value, Timestamp)
VALUES (@VarA2ToolStatus, 'ON', CURRENT_TIMESTAMP);

INSERT INTO OpenFactoryLink (VariableId, AssetUuid, DataItemId)
VALUES (@VarA2ToolStatus, 'IVAC', 'A2ToolPlus');

INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('SpindlePositionX', @TypePosition, '7');
DECLARE @VarSpindlePosX INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value, Timestamp)
VALUES (@VarSpindlePosX, 2.5, CURRENT_TIMESTAMP);

INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('SpindlePositionY', @TypePosition, '7');
DECLARE @VarSpindlePosY INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value, Timestamp)
VALUES (@VarSpindlePosY, 0.0, CURRENT_TIMESTAMP);

INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('SpindlePositionZ', @TypePosition, '7');
DECLARE @VarSpindlePosZ INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value, Timestamp)
VALUES (@VarSpindlePosZ, 1.2, CURRENT_TIMESTAMP);

INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('SpindleAngleX', @TypeAngle, '7');
DECLARE @VarSpindleAngleX INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value, Timestamp)
VALUES (@VarSpindleAngleX, 0.0, CURRENT_TIMESTAMP);

INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('SpindleAngleY', @TypeAngle, '7');
DECLARE @VarSpindleAngleY INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value, Timestamp)
VALUES (@VarSpindleAngleY, 0.0, CURRENT_TIMESTAMP);

INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('SpindleAngleZ', @TypeAngle, '7');
DECLARE @VarSpindleAngleZ INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value, Timestamp)
VALUES (@VarSpindleAngleZ, 0.0, CURRENT_TIMESTAMP);

--A3ToolPlus
INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('A3ToolStatus', @TypeToolStatus, '8');
DECLARE @VarA3ToolStatus INT = SCOPE_IDENTITY();

INSERT INTO StrValue (VariableId, Value, Timestamp)
VALUES (@VarA3ToolStatus, 'OFF', CURRENT_TIMESTAMP);

INSERT INTO OpenFactoryLink (VariableId, AssetUuid, DataItemId)
VALUES (@VarA3ToolStatus, 'IVAC', 'A3ToolPlus');

INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('LathePositionX', @TypePosition, '8');
DECLARE @VarLathePosX INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value, Timestamp)
VALUES (@VarLathePosX, 3.5, CURRENT_TIMESTAMP);

INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('LathePositionY', @TypePosition, '8');
DECLARE @VarLathePosY INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value, Timestamp)
VALUES (@VarLathePosY, 0.0, CURRENT_TIMESTAMP);

INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('LathePositionZ', @TypePosition, '8');
DECLARE @VarLathePosZ INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value, Timestamp)
VALUES (@VarLathePosZ, 1.2, CURRENT_TIMESTAMP);

INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('LatheAngleX', @TypeAngle, '8');
DECLARE @VarLatheAngleX INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value, Timestamp)
VALUES (@VarLatheAngleX, 0.0, CURRENT_TIMESTAMP);

INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('LatheAngleY', @TypeAngle, '8');
DECLARE @VarLatheAngleY INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value, Timestamp)
VALUES (@VarLatheAngleY, 0.0, CURRENT_TIMESTAMP);

INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('LatheAngleZ', @TypeAngle, '8');
DECLARE @VarLatheAngleZ INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value, Timestamp)
VALUES (@VarLatheAngleZ, 0.0, CURRENT_TIMESTAMP);

--A2BlastGate
INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('A2BlastGateStatus', @TypeGateStatus, '9');
DECLARE @VarA2BlastGate INT = SCOPE_IDENTITY();

INSERT INTO StrValue (VariableId, Value, Timestamp)
VALUES (@VarA2BlastGate, 'OPEN', CURRENT_TIMESTAMP);

INSERT INTO OpenFactoryLink (VariableId, AssetUuid, DataItemId)
VALUES (@VarA2BlastGate, 'IVAC', 'A2BlastGate');

INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('A2GatePositionX', @TypePosition, '9');
DECLARE @VarA2GatePosX INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value, Timestamp)
VALUES (@VarA2GatePosX, 2.5, CURRENT_TIMESTAMP);

INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('A2GatePositionY', @TypePosition, '9');
DECLARE @VarA2GatePosY INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value, Timestamp)
VALUES (@VarA2GatePosY, 1.0, CURRENT_TIMESTAMP);

INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('A2GatePositionZ', @TypePosition, '9');
DECLARE @VarA2GatePosZ INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value, Timestamp)
VALUES (@VarA2GatePosZ, 1.2, CURRENT_TIMESTAMP);

INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('A2GateAngleX', @TypeAngle, '9');
DECLARE @VarA2GateAngleX INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value, Timestamp)
VALUES (@VarA2GateAngleX, 0.0, CURRENT_TIMESTAMP);

INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('A2GateAngleY', @TypeAngle, '9');
DECLARE @VarA2GateAngleY INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value, Timestamp)
VALUES (@VarA2GateAngleY, 0.0, CURRENT_TIMESTAMP);

INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('A2GateAngleZ', @TypeAngle, '9');
DECLARE @VarA2GateAngleZ INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value, Timestamp)
VALUES (@VarA2GateAngleZ, 0.0, CURRENT_TIMESTAMP);

--A3BlastGate
INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('A3BlastGateStatus', @TypeGateStatus, '10');
DECLARE @VarA3BlastGate INT = SCOPE_IDENTITY();

INSERT INTO StrValue (VariableId, Value, Timestamp)
VALUES (@VarA3BlastGate, 'CLOSED', CURRENT_TIMESTAMP);

INSERT INTO OpenFactoryLink (VariableId, AssetUuid, DataItemId)
VALUES (@VarA3BlastGate, 'IVAC', 'A3BlastGate');

INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('A3GatePositionX', @TypePosition, '10');
DECLARE @VarA3GatePosX INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value, Timestamp)
VALUES (@VarA3GatePosX, 2.5, CURRENT_TIMESTAMP);

INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('A3GatePositionY', @TypePosition, '10');
DECLARE @VarA3GatePosY INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value, Timestamp)
VALUES (@VarA3GatePosY, 1.0, CURRENT_TIMESTAMP);

INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('A3GatePositionZ', @TypePosition, '10');
DECLARE @VarA3GatePosZ INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value, Timestamp)
VALUES (@VarA3GatePosZ, 1.2, CURRENT_TIMESTAMP);

INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('A3GateAngleX', @TypeAngle, '10');
DECLARE @VarA3GateAngleX INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value, Timestamp)
VALUES (@VarA3GateAngleX, 0.0, CURRENT_TIMESTAMP);

INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('A3GateAngleY', @TypeAngle, '10');
DECLARE @VarA3GateAngleY INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value, Timestamp)
VALUES (@VarA3GateAngleY, 0.0, CURRENT_TIMESTAMP);

INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('A3GateAngleZ', @TypeAngle, '10');
DECLARE @VarA3GateAngleZ INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value, Timestamp)
VALUES (@VarA3GateAngleZ, 0.0, CURRENT_TIMESTAMP);