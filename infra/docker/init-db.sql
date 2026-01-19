-- Initialize tennis schema for Tournament Studio
CREATE SCHEMA IF NOT EXISTS tennis;

-- Grant permissions
GRANT ALL ON SCHEMA tennis TO tennis_studio;
GRANT ALL ON ALL TABLES IN SCHEMA tennis TO tennis_studio;
GRANT ALL ON ALL SEQUENCES IN SCHEMA tennis TO tennis_studio;

-- Set search path
ALTER DATABASE tennis_studio SET search_path TO tennis, public;

