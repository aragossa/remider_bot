CREATE TABLE GMT (ID INT, GMT VARCHAR);

CREATE TABLE "messages" (
	"id"	integer PRIMARY KEY AUTOINCREMENT,
	"user_id"	integer,
	"message_id"	integer,
	"message_text"	text,
	"notifi_datetime"	datetime,
	"status"	INTEGER,
	"content_type"	INTEGER
);