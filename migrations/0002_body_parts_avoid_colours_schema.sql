-- 0002_body_parts_avoid_colours_schema.sql
-- Reference tables: house/sign -> body part (Kalapurusha) and avoid-colours (per lagna, per planet).
-- SCHEMA ONLY. Seed rows are in 0003_body_parts_avoid_colours_seed.sql. No birth data here.
-- Numbered 0002 because PR #2 owns 0001_verified_charts.sql.
-- NOT applied to any live database by the PR that adds it. To apply (owner / deploy step):
--   wrangler d1 execute jyotish-rules --remote --file migrations/0002_body_parts_avoid_colours_schema.sql
-- Every statement is idempotent (IF NOT EXISTS). Every row is status 'DEFAULT, owner to confirm' (tradition claim, not measured).

CREATE TABLE IF NOT EXISTS ref_house_body_part (
  house_no      INTEGER PRIMARY KEY CHECK (house_no BETWEEN 1 AND 12),  -- 1 = Aries/head ... 12 = Pisces/feet
  natural_sign  TEXT NOT NULL UNIQUE,                                   -- the natural-zodiac sign of this house number
  primary_part  TEXT NOT NULL,                                          -- classical Kalapurusha limb
  extended_parts TEXT NOT NULL,                                         -- JSON array of further organs
  basis         TEXT NOT NULL,
  status        TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ref_lagna_avoid_colour (
  lagna_no      INTEGER NOT NULL CHECK (lagna_no BETWEEN 1 AND 12),     -- 1 = Aries lagna ... 12 = Pisces lagna
  lagna_sign    TEXT NOT NULL,
  avoid_order   INTEGER NOT NULL,                                       -- order inside one lagna (house 6, 8, 12 lords)
  avoid_planet  TEXT NOT NULL,
  avoid_colour  TEXT NOT NULL,                                          -- from the owner's planet-colour table
  houses_lorded TEXT NOT NULL,                                          -- JSON array of houses this planet lords for this lagna
  reason        TEXT NOT NULL,
  status        TEXT NOT NULL,
  PRIMARY KEY (lagna_no, avoid_planet)
);

CREATE TABLE IF NOT EXISTS ref_planet_avoid_colour (
  planet_no     INTEGER NOT NULL CHECK (planet_no BETWEEN 0 AND 6),     -- engine id: Sun 0 ... Saturn 6
  planet        TEXT NOT NULL,
  enemy_no      INTEGER NOT NULL CHECK (enemy_no BETWEEN 0 AND 6),
  enemy_planet  TEXT NOT NULL,
  avoid_colour  TEXT NOT NULL,                                          -- colour of the enemy planet (owner table)
  reason        TEXT NOT NULL,
  status        TEXT NOT NULL,
  PRIMARY KEY (planet_no, enemy_no)
);
