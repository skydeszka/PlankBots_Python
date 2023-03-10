CREATE TABLE IF NOT EXISTS "LocalData" (
	"ServerID"	TEXT NOT NULL,
	"ID"	TEXT NOT NULL,
	"EXP"	INTEGER NOT NULL,
	"BALANCE"	INTEGER NOT NULL,
	PRIMARY KEY("ID","ServerID")
);

CREATE TABLE IF NOT EXISTS "GlobalData" (
	"ID"	TEXT NOT NULL PRIMARY KEY,
	"EXP"	INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS "UnhandledErrors" (
	"ID"	TEXT NOT NULL PRIMARY KEY,
	"MESSAGE"	TEXT NOT NULL,
	"ERROR"	TEXT NOT NULL,
	"TRACEBACK" TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS "ServerData" (
	"ID"	INTEGER NOT NULL,
	"LVLChannel"	INTEGER,
	"TrafficChannel"	INTEGER,
	PRIMARY KEY("ID")
);
