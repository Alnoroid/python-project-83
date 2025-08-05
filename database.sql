DROP TABLE IF EXISTS urls CASCADE;
CREATE TABLE urls (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) UNIQUE NOT NULL,
  created_at TIMESTAMP
);

DROP TABLE IF EXISTS url_checks CASCADE;
CREATE TABLE url_checks (
  id SERIAL PRIMARY KEY,
  url_id int REFERENCES urls (id),
  status_code integer,
  h1 text,
  title text,
  description text,
  created_at TIMESTAMP
);