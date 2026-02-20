-- Migration: add `mbid` column to `trending_artists`
-- Run this on your Postgres/Supabase database to add the MBID field.

ALTER TABLE public.trending_artists
ADD COLUMN IF NOT EXISTS mbid character varying;

-- Optional: create an index on mbid if you'll query by it
-- CREATE INDEX IF NOT EXISTS idx_trending_artists_mbid ON public.trending_artists (mbid);
