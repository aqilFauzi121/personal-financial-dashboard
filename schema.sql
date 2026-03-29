-- ============================================================
-- ARSITEK FINANSIAL PRIBADI — DATABASE SCHEMA LENGKAP v2
-- Termasuk fitur Multi-Wallet
-- ============================================================
-- Jalankan file ini HANYA untuk setup database dari nol.
-- Jika database sudah ada, gunakan migration_add_wallets.sql.
-- ============================================================


-- ── 1. TABEL WALLETS ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.wallets (
  id              UUID      DEFAULT uuid_generate_v4() PRIMARY KEY,
  name            TEXT      NOT NULL,
  type            TEXT      NOT NULL CHECK (type IN ('cash', 'bank', 'ewallet', 'investment')),
  initial_balance NUMERIC   NOT NULL DEFAULT 0,
  is_investment   BOOLEAN   NOT NULL DEFAULT FALSE,
  is_active       BOOLEAN   NOT NULL DEFAULT TRUE,
  created_at      TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW())
);

INSERT INTO public.wallets (name, type, initial_balance, is_investment)
  VALUES ('Cash', 'cash', 0, FALSE)
  ON CONFLICT DO NOTHING;


-- ── 2. TABEL TRANSAKSI ───────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.transactions (
  id         UUID      DEFAULT uuid_generate_v4() PRIMARY KEY,
  date       DATE      NOT NULL DEFAULT CURRENT_DATE,
  type       TEXT      NOT NULL CHECK (type IN ('Pemasukan', 'Pengeluaran')),
  amount     NUMERIC   NOT NULL CHECK (amount > 0),
  category   TEXT      NOT NULL,
  notes      TEXT,
  wallet_id  UUID      REFERENCES public.wallets(id) ON DELETE SET NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW())
);

CREATE INDEX IF NOT EXISTS idx_transactions_wallet_id
  ON public.transactions(wallet_id);


-- ── 3. TABEL ENVELOPES (AMPLOP) ──────────────────────────────
CREATE TABLE IF NOT EXISTS public.envelopes (
  id                    UUID    DEFAULT uuid_generate_v4() PRIMARY KEY,
  name                  TEXT    NOT NULL UNIQUE,
  allocation_percentage NUMERIC NOT NULL CHECK (allocation_percentage >= 0 AND allocation_percentage <= 100),
  created_at            TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW())
);

INSERT INTO public.envelopes (name, allocation_percentage)
  VALUES
    ('Dana Darurat',       20),
    ('Operasional',        40),
    ('Pajak & Biaya Admin',20),
    ('Self-Reward',        20)
  ON CONFLICT (name) DO NOTHING;


-- ── 4. TABEL PENDING INCOMES (PIUTANG KLIEN) ─────────────────
CREATE TABLE IF NOT EXISTS public.pending_incomes (
  id          UUID    DEFAULT uuid_generate_v4() PRIMARY KEY,
  client_name TEXT    NOT NULL,
  amount      NUMERIC NOT NULL CHECK (amount > 0),
  due_date    DATE    NOT NULL,
  status      TEXT    NOT NULL CHECK (status IN ('Pending', 'Cair')),
  created_at  TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW())
);


-- ── 5. TABEL WALLET_TRANSFERS ─────────────────────────────────
CREATE TABLE IF NOT EXISTS public.wallet_transfers (
  id             UUID      DEFAULT uuid_generate_v4() PRIMARY KEY,
  from_wallet_id UUID      NOT NULL REFERENCES public.wallets(id) ON DELETE RESTRICT,
  to_wallet_id   UUID      NOT NULL REFERENCES public.wallets(id) ON DELETE RESTRICT,
  amount         NUMERIC   NOT NULL CHECK (amount > 0),
  notes          TEXT,
  date           DATE      NOT NULL DEFAULT CURRENT_DATE,
  created_at     TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()),
  CONSTRAINT no_self_transfer CHECK (from_wallet_id <> to_wallet_id)
);

CREATE INDEX IF NOT EXISTS idx_wallet_transfers_from
  ON public.wallet_transfers(from_wallet_id);

CREATE INDEX IF NOT EXISTS idx_wallet_transfers_to
  ON public.wallet_transfers(to_wallet_id);


-- ── 6. FUNCTION: ATOMIK PENCAIRAN FAKTUR ─────────────────────
CREATE OR REPLACE FUNCTION mark_income_paid(
  p_income_id       UUID,
  p_client_name     TEXT,
  p_amount          NUMERIC,
  p_due_date        DATE,
  p_tax_percentage  NUMERIC DEFAULT 0,
  p_wallet_id       UUID    DEFAULT NULL
)
RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
  UPDATE public.pending_incomes
    SET status = 'Cair'
    WHERE id = p_income_id;

  INSERT INTO public.transactions (date, type, amount, category, notes, wallet_id)
    VALUES (
      p_due_date,
      'Pemasukan',
      p_amount,
      'Pencairan Faktur',
      'Dari: ' || p_client_name,
      p_wallet_id
    );

  IF p_tax_percentage > 0 THEN
    INSERT INTO public.transactions (date, type, amount, category, notes, wallet_id)
      VALUES (
        p_due_date,
        'Pengeluaran',
        p_amount * (p_tax_percentage / 100),
        'Pajak & Biaya Admin',
        'Pemotongan pajak ' || p_tax_percentage || '% faktur ' || p_client_name,
        p_wallet_id
      );
  END IF;
END;
$$;


-- ── 7. FUNCTION: ATOMIK TRANSFER ANTAR WALLET ────────────────
CREATE OR REPLACE FUNCTION transfer_between_wallets(
  p_from_wallet_id  UUID,
  p_to_wallet_id    UUID,
  p_amount          NUMERIC,
  p_date            DATE,
  p_notes           TEXT DEFAULT ''
)
RETURNS void
LANGUAGE plpgsql
AS $$
DECLARE
  v_from_name TEXT;
  v_to_name   TEXT;
BEGIN
  SELECT name INTO v_from_name FROM public.wallets WHERE id = p_from_wallet_id;
  SELECT name INTO v_to_name   FROM public.wallets WHERE id = p_to_wallet_id;

  INSERT INTO public.transactions (date, type, amount, category, notes, wallet_id)
    VALUES (
      p_date,
      'Pengeluaran',
      p_amount,
      'Transfer Keluar',
      'Transfer ke ' || v_to_name || CASE WHEN p_notes <> '' THEN ' — ' || p_notes ELSE '' END,
      p_from_wallet_id
    );

  INSERT INTO public.transactions (date, type, amount, category, notes, wallet_id)
    VALUES (
      p_date,
      'Pemasukan',
      p_amount,
      'Transfer Masuk',
      'Transfer dari ' || v_from_name || CASE WHEN p_notes <> '' THEN ' — ' || p_notes ELSE '' END,
      p_to_wallet_id
    );

  INSERT INTO public.wallet_transfers (from_wallet_id, to_wallet_id, amount, notes, date)
    VALUES (p_from_wallet_id, p_to_wallet_id, p_amount, p_notes, p_date);
END;
$$;


-- ── 8. ROW LEVEL SECURITY ─────────────────────────────────────
ALTER TABLE public.transactions    ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.envelopes       ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.pending_incomes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.wallets         ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.wallet_transfers ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_only" ON public.transactions
  FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "service_role_only" ON public.envelopes
  FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "service_role_only" ON public.pending_incomes
  FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "service_role_only" ON public.wallets
  FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "service_role_only" ON public.wallet_transfers
  FOR ALL USING (auth.role() = 'service_role');