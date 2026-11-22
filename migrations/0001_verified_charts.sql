-- 0001_verified_charts.sql
-- Verified reference charts captured from the owner's own logged-in
-- jagannathahora.com account (people: RAJAT, PALLAVI, ESHANI, PEHU).
--
-- SCHEMA ONLY. This file holds no birth data. The data is loaded straight into
-- the Cloudflare D1 database `jyotish-rules` by core/verified_charts.py from the
-- private folder data_private/ (git-ignored). Family birth data NEVER goes in git
-- (CLAUDE.md hard rule).
--
-- Apply with:  wrangler d1 execute jyotish-rules --remote --file migrations/0001_verified_charts.sql
-- (core/verified_charts.py --init applies the same statements through the D1 HTTP API).
-- Every statement is idempotent (IF NOT EXISTS).

-- One row per person: birth data exactly as shown on the site.
CREATE TABLE IF NOT EXISTS vc_person (
  person_key        TEXT PRIMARY KEY,            -- RAJAT | PALLAVI | ESHANI | PEHU
  display_name      TEXT NOT NULL,               -- name field on the site
  saved_chart_label TEXT,                        -- label in the site's saved-charts list
  gender            TEXT,
  dob_iso           TEXT,                        -- YYYY-MM-DD
  dob_site_text     TEXT,                        -- as shown (DD/MM/YYYY)
  tob_24h           TEXT,                        -- HH:MM (the site shows minutes only)
  tob_site_text     TEXT,                        -- as shown (e.g. 6:15 AM)
  place_city        TEXT,
  place_state       TEXT,
  latitude          REAL,
  longitude         REAL,
  timezone_site_text TEXT,                       -- as shown (+05:30 or Auto)
  source_url        TEXT NOT NULL,
  verified_source   TEXT NOT NULL DEFAULT 'jagannathahora.com',
  captured_at       TEXT NOT NULL,               -- ISO-8601 UTC
  form_raw          TEXT,                        -- raw form dump
  doubts_json       TEXT                         -- list of open questions about the birth data
);

-- Every screen / tab / dropdown view, as text (one row per view).
CREATE TABLE IF NOT EXISTS vc_screen (
  person_key   TEXT NOT NULL,
  screen_key   TEXT NOT NULL,                    -- e.g. details:Key Info, horoscope:chart:Navamsa
  page_path    TEXT,                             -- site route, e.g. /details
  source_url   TEXT NOT NULL,
  captured_at  TEXT NOT NULL,
  char_count   INTEGER NOT NULL,
  n_chunks     INTEGER NOT NULL,                 -- body text is split into vc_screen_chunk rows
  tables_json  TEXT,                             -- tab-separated tables on the screen, as arrays (small screens only)
  PRIMARY KEY (person_key, screen_key)
);
CREATE TABLE IF NOT EXISTS vc_screen_chunk (
  person_key TEXT NOT NULL,
  screen_key TEXT NOT NULL,
  seq        INTEGER NOT NULL,
  chunk      TEXT NOT NULL,
  PRIMARY KEY (person_key, screen_key, seq)
);

-- Planet / sensitive-point positions (Details > Key Info).
CREATE TABLE IF NOT EXISTS vc_body_position (
  person_key     TEXT NOT NULL,
  grp            INTEGER NOT NULL,               -- table group order on the page
  body           TEXT NOT NULL,
  longitude_text TEXT,                           -- degrees within sign, as shown (e.g. 6°42')
  deg            INTEGER,
  minute         INTEGER,
  nakshatra      TEXT,
  pada           INTEGER,
  rasi           TEXT,
  navamsha       TEXT,
  PRIMARY KEY (person_key, grp, body)
);

-- Sign + degree of every body in every divisional chart (Details > All Bodies).
CREATE TABLE IF NOT EXISTS vc_body_varga (
  person_key TEXT NOT NULL,
  grp        INTEGER NOT NULL,
  body       TEXT NOT NULL,
  varga      TEXT NOT NULL,                      -- D-1, D-9, ...
  sign       TEXT,                               -- 2-letter code as shown (Le, Ar, ...)
  deg        INTEGER,
  minute     INTEGER,
  raw        TEXT,
  PRIMARY KEY (person_key, grp, body, varga)
);

-- Dasha periods (flat list as shown, nesting level derived by date containment).
CREATE TABLE IF NOT EXISTS vc_dasha_period (
  person_key   TEXT NOT NULL,
  screen_key   TEXT NOT NULL,                    -- which dasha screen it came from
  seq          INTEGER NOT NULL,
  level        INTEGER NOT NULL,                 -- 1 = maha, 2 = antar, 3 = pratyantar ...
  lord         TEXT NOT NULL,
  start_text   TEXT,
  end_text     TEXT,
  duration_text TEXT,
  is_current   INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (person_key, screen_key, seq)
);

-- Screenshot files linked to person + screen. Image bytes are kept (base64, chunked) so the
-- database is self-contained; the original files stay in data_private/ (git-ignored).
CREATE TABLE IF NOT EXISTS vc_screenshot (
  person_key  TEXT NOT NULL,
  file_name   TEXT NOT NULL,
  screen_name TEXT NOT NULL,
  sha256      TEXT NOT NULL,
  bytes       INTEGER NOT NULL,
  n_chunks    INTEGER NOT NULL,
  source_url  TEXT NOT NULL,
  captured_at TEXT NOT NULL,
  PRIMARY KEY (person_key, file_name)
);
CREATE TABLE IF NOT EXISTS vc_screenshot_chunk (
  person_key TEXT NOT NULL,
  file_name  TEXT NOT NULL,
  seq        INTEGER NOT NULL,
  b64        TEXT NOT NULL,
  PRIMARY KEY (person_key, file_name, seq)
);

CREATE INDEX IF NOT EXISTS idx_vc_screen_person ON vc_screen(person_key);
CREATE INDEX IF NOT EXISTS idx_vc_varga_body ON vc_body_varga(person_key, body);
