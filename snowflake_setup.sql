CREATE DATABASE IF NOT EXISTS AGGIE_DECISION_DESK;
USE DATABASE AGGIE_DECISION_DESK;
CREATE SCHEMA IF NOT EXISTS PUBLIC;
USE SCHEMA PUBLIC;

CREATE TABLE IF NOT EXISTS CAMPUS_FACTS (
  ID VARCHAR, CATEGORY VARCHAR, NAME VARCHAR, DESCRIPTION VARCHAR,
  LOCATION VARCHAR, PRICE FLOAT, OPEN_TIME VARCHAR, CLOSE_TIME VARCHAR,
  TAGS VARCHAR, SOURCE_URL VARCHAR, UPDATED_AT DATE
);

INSERT INTO CAMPUS_FACTS VALUES
('DIN-001','Dining','The Commons Dining Hall','All-you-care-to-eat dining hall with vegetarian and vegan stations.','Commons Dining Hall, Northside',12.50,'07:00','21:00','dining, vegetarian, vegan, meal plan, northside','https://dining.tamu.edu/','2026-11-07'),
('DIN-002','Dining','The Grill at MSC','Quick-service burgers, sandwiches, salads, and fries inside the Memorial Student Center.','Memorial Student Center',10.00,'10:30','20:00','dining, quick, burger, sandwich, central campus','https://dining.tamu.edu/','2026-11-07'),
('DIN-003','Dining','Houston Street Cafe','Coffee, smoothies, wraps, and grab-and-go meals with indoor seating.','Zachry Engineering Center',8.50,'07:30','17:00','dining, coffee, smoothie, wrap, zachry, indoor','https://dining.tamu.edu/','2026-11-07'),
('LOC-001','Facility','Zachry Engineering Center','Engineering classrooms, labs, study spaces, and indoor seating.','3167 TAMU',0,'06:00','23:00','zachry, engineering, study, indoor, classroom','https://engineering.tamu.edu/','2026-11-07'),
('TRN-001','Transit','Route 12: Bonfire','Campus shuttle route connecting the MSC, Zachry, and north campus stops.','MSC ↔ Zachry ↔ North Campus',0,'07:00','22:00','bus, shuttle, transit, msc, zachry, north campus','https://transport.tamu.edu/Bus/routes.aspx','2026-11-07'),
('WTH-001','Weather','Campus weather snapshot','Hot afternoon conditions expected. Hydrate, use shade, and prefer indoor routes when possible.','College Station campus',0,'12:00','18:00','weather, heat, hot, hydration, shade, afternoon','https://weather.tamu.edu/','2026-11-07'),
('RES-001','Resource','Student Counseling & Mental Health','Confidential counseling, crisis support, and mental health resources for students.','Student Services Building',0,'08:00','17:00','wellbeing, counseling, mental health, student support','https://caps.tamu.edu/','2026-11-07'),
('EVT-001','Event','Engineering Career Mixer','Employer networking event for engineering students. Business casual recommended.','MSC Bethancourt Ballroom',0,'17:30','19:30','event, career, engineering, networking, msc','https://calendar.tamu.edu/','2026-11-07');
