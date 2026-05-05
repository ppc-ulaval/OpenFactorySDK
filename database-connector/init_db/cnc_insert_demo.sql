USE mytest;
GO

INSERT INTO Room (Id, Nom, Largeur, Longueur, Hauteur)
VALUES ('room-001', 'Assembly Room', 15.0, 10.0, 5.0);


INSERT INTO EquipmentType (Nom, Description)
VALUES 
('Test', 'Test'),
('CNC_Structure', 'Test'),
('CNC_Bridge', 'Test'),
('CNC_Rack', 'Test'),
('CNC_Spindle', 'Test');

INSERT INTO Manufacturer (Nom, Description)
VALUES 
('Test', 'Test');


INSERT INTO Model (Nom, Description)
VALUES 
('Test', 'Test');


INSERT INTO Type (Nom, Description, Units)
VALUES 
('Position', 'A measured or calculated position of a component element as reported by a piece of equipment.', 'Millimiter'),
('Angle', 'The measurement of angular position.', 'Degree'),
('Temperature', 'Current temperature', 'Celsius'),
('ActuatorState', 'The operational state of an apparatus for moving or controlling a mechanism or system.', NULL),
('Load', 'The measurement of the actual versus the standard rating of a piece of equipment.', 'Percent'),
('RotaryVelocity', 'The measurement of the rotational speed of a rotary axis. ', 'RPM');
GO

-- Get lookup IDs
DECLARE @Type INT = (SELECT Id FROM EquipmentType WHERE Nom = 'Test');
DECLARE @TypeCNC_Structure INT = (SELECT Id FROM EquipmentType WHERE Nom = 'CNC_Structure');
DECLARE @TypeCNC_Bridge INT = (SELECT Id FROM EquipmentType WHERE Nom = 'CNC_Bridge');
DECLARE @TypeCNC_Rack INT = (SELECT Id FROM EquipmentType WHERE Nom = 'CNC_Rack');
DECLARE @TypeCNC_Spindle INT = (SELECT Id FROM EquipmentType WHERE Nom = 'CNC_Spindle');

DECLARE @Mfr INT = (SELECT Id FROM Manufacturer WHERE Nom = 'Test');
DECLARE @Model INT = (SELECT Id FROM Model WHERE Nom = 'Test');

-- Insert Equipment
INSERT INTO Equipment (Id, ParentEquipmentId, EquipmentTypeId, ManufacturerId, ModelId, RoomId, Nom, PrefabKey, SerialNumber, PurchaseDate)
VALUES 
('1', NULL, @Type, @Mfr, @Model, 'room-001', 'CNC Machine', 'CNC_Prefab', 'Test', '2023-02-15'),
('3', NULL, @Type, @Mfr, @Model, 'room-001', 'Robot', 'Robot_Prefab', 'Test', '2023-02-15'),
('4', NULL, @TypeCNC_Structure, @Mfr, @Model, 'room-001', 'CNC_Structure', 'CNC_Structure', 'Test', '2025-07-11');

INSERT INTO Equipment (Id, ParentEquipmentId, EquipmentTypeId, ManufacturerId, ModelId, RoomId, Nom, PrefabKey, SerialNumber, PurchaseDate)
VALUES 
('2', '1', @Type, @Mfr, @Model, 'room-001', 'CNC Bridge', 'CNC_Bridge_Prefab', 'Test', '2023-02-15'),
('5', '4', @TypeCNC_Bridge, @Mfr, @Model, 'room-001', 'CNC_Bridge', NULL, 'Test', '2025-07-11'),
('6', '5', @TypeCNC_Rack, @Mfr, @Model, 'room-001', 'CNC_Rack', NULL, 'Test', '2025-07-11'),
('7', '6', @TypeCNC_Spindle, @Mfr, @Model, 'room-001', 'CNC_Spindle', NULL, 'Test', '2025-07-11');

-- Get Type IDs
DECLARE @TypeTemp INT = (SELECT Id FROM Type WHERE Nom = 'Temperature');
DECLARE @TypeStatus INT = (SELECT Id FROM Type WHERE Nom = 'ActuatorState');
DECLARE @TypeLoad INT = (SELECT Id FROM Type WHERE Nom = 'Load');
DECLARE @TypeSpeed INT = (SELECT Id FROM Type WHERE Nom = 'RotaryVelocity');
DECLARE @TypePos INT = (SELECT Id FROM Type WHERE Nom = 'Position');
DECLARE @TypeRot INT = (SELECT Id FROM Type WHERE Nom = 'Angle');

-- Temperature (float) for Equipment 1
INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('1', 'test', @TypeTemp);
DECLARE @VarTemp INT = SCOPE_IDENTITY();

INSERT INTO IntValue (VariableId, Value)
VALUES (@VarTemp, 8);

INSERT INTO IntValue (VariableId, Value)
VALUES (@VarTemp, 10);

INSERT INTO IntValue (VariableId, Value)
VALUES (@VarTemp, 12);

-- Status (string) for Equipment 1
INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('1', 'test', @TypeStatus);
DECLARE @VarStatus INT = SCOPE_IDENTITY();

INSERT INTO StrValue (VariableId, Value)
VALUES (@VarStatus, 'ACTIVE');

-- Load (float) for Equipment 2
INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('2', 'test', @TypeLoad);
DECLARE @VarLoad INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@VarLoad, 120.5);

-- Succion state for Equipment 4
INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('4', 'CNCStructureSuccionState', @TypeStatus);
DECLARE @VarSuccion INT = SCOPE_IDENTITY();

INSERT INTO StrValue (VariableId, Value)
VALUES (@VarSuccion, 'INACTIVE');

INSERT INTO OpenFactoryLink (VariableId, AssetUuid, DataItemId)
VALUES (@VarSuccion, 'CNC123', 'vacuum_status');

-- Speed for Equipment 7
INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('7', 'test', @TypeSpeed);
DECLARE @VarSpeed INT = SCOPE_IDENTITY();

INSERT INTO IntValue (VariableId, Value)
VALUES (@VarSpeed, 0);

INSERT INTO OpenFactoryLink (VariableId, AssetUuid, DataItemId)
VALUES (@VarSpeed, 'CNC123', 'spindle_speed');

-- CNC Machine Transform (Equipment 1)
INSERT INTO Variable (EquipmentId, Nom, TypeId) 
VALUES ('1', 'PositionX', @TypePos);
DECLARE @Var1PX INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var1PX, 2.5);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('1', 'PositionY', @TypePos);
DECLARE @Var1PY INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var1PY, 0.0);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('1', 'PositionZ', @TypePos);
DECLARE @Var1PZ INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var1PZ, 1.2);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('1', 'RotationX', @TypeRot);
DECLARE @Var1RX INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var1RX, 0.0);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('1', 'RotationY', @TypeRot);
DECLARE @Var1RY INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var1RY, 0.0);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('1', 'RotationZ', @TypeRot);
DECLARE @Var1RZ INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var1RZ, 0.0);

-- CNC Bridge Transform (Equipment 2)
INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('2', 'PositionX', @TypePos);
DECLARE @Var2PX INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var2PX, 2.5);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('2', 'PositionY', @TypePos);
DECLARE @Var2PY INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var2PY, 1.5);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('2', 'PositionZ', @TypePos);
DECLARE @Var2PZ INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var2PZ, 1.2);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('2', 'RotationX', @TypeRot);
DECLARE @Var2RX INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var2RX, 0.0);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('2', 'RotationY', @TypeRot);
DECLARE @Var2RY INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var2RY, 0.0);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('2', 'RotationZ', @TypeRot);
DECLARE @Var2RZ INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var2RZ, 0.0);

-- Robot Transform (Equipment 3)
INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('3', 'PositionX', @TypePos);
DECLARE @Var3PX INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var3PX, 0.0);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('3', 'PositionY', @TypePos);
DECLARE @Var3PY INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var3PY, 0.0);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('3', 'PositionZ', @TypePos);
DECLARE @Var3PZ INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var3PZ, 0.0);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('3', 'RotationX', @TypeRot);
DECLARE @Var3RX INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var3RX, 0.0);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('3', 'RotationY', @TypeRot);
DECLARE @Var3RY INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var3RY, 0.0);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('3', 'RotationZ', @TypeRot);
DECLARE @Var3RZ INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var3RZ, 0.0);

-- CNC_Structure Transform (Equipment 4)
INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('4', 'PositionX', @TypePos);
DECLARE @Var4PX INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var4PX, 3.65);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('4', 'PositionY', @TypePos);
DECLARE @Var4PY INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var4PY, 0.8);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('4', 'PositionZ', @TypePos);
DECLARE @Var4PZ INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var4PZ, 5.12);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('4', 'RotationX', @TypeRot);
DECLARE @Var4RX INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var4RX, 0.0);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('4', 'RotationY', @TypeRot);
DECLARE @Var4RY INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var4RY, 270.0);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('4', 'RotationZ', @TypeRot);
DECLARE @Var4RZ INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var4RZ, 0.0);

-- CNC_Bridge Transform (Equipment 5)
INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('5', 'PositionX', @TypePos);
DECLARE @Var5PX INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var5PX, 5.0);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('5', 'PositionY', @TypePos);
DECLARE @Var5PY INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var5PY, -100.0);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('5', 'PositionZ', @TypePos);
DECLARE @Var5PZ INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var5PZ, -1000.0);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('5', 'RotationX', @TypeRot);
DECLARE @Var5RX INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var5RX, 0.0);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('5', 'RotationY', @TypeRot);
DECLARE @Var5RY INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var5RY, 0.0);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('5', 'RotationZ', @TypeRot);
DECLARE @Var5RZ INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var5RZ, 0.0);

-- CNC_Rack Transform (Equipment 6)
INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('6', 'PositionX', @TypePos);
DECLARE @Var6PX INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var6PX, -500.0);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('6', 'PositionY', @TypePos);
DECLARE @Var6PY INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var6PY, 575.0);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('6', 'PositionZ', @TypePos);
DECLARE @Var6PZ INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var6PZ, -175.0);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('6', 'RotationX', @TypeRot);
DECLARE @Var6RX INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var6RX, 0.0);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('6', 'RotationY', @TypeRot);
DECLARE @Var6RY INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var6RY, 0.0);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('6', 'RotationZ', @TypeRot);
DECLARE @Var6RZ INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var6RZ, 0.0);

-- CNC_Spindle Transform (Equipment 7)
INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('7', 'PositionX', @TypePos);
DECLARE @Var7PX INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var7PX, 0.0);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('7', 'PositionY', @TypePos);
DECLARE @Var7PY INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var7PY, -275.0);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('7', 'PositionZ', @TypePos);
DECLARE @Var7PZ INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var7PZ, 240.0);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('7', 'RotationX', @TypeRot);
DECLARE @Var7RX INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var7RX, 0.0);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('7', 'RotationY', @TypeRot);
DECLARE @Var7RY INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var7RY, 0.0);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('7', 'RotationZ', @TypeRot);
DECLARE @Var7RZ INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var7RZ, 0.0);