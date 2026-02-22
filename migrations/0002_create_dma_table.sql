CREATE TABLE dma_top_artists (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    country TEXT NOT NULL,
    artist_name TEXT NOT NULL,
    listeners INTEGER,
    mbid TEXT,
    rank INTEGER NOT NULL,
    captured_at DATE DEFAULT CURRENT_DATE
);

-- Crucial: Prevents duplicate entries for the same artist in the same country on the same day
CREATE UNIQUE INDEX dma_country_artist_date_idx ON dma_top_artists (country, artist_name, captured_at);