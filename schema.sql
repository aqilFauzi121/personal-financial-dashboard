-- ============================================
-- ARSITEK FINANSIAL PRIBADI — DATABASE SCHEMA
-- ============================================
-- Jalankan file ini sekali di Supabase SQL Editor
-- untuk setup database dari awal.
-- ============================================


-- 1. TABEL TRANSAKSI
-- ============================================
CREATE TABLE IF NOT EXISTS public.transactions (
  id         UUID      DEFAULT uuid_generate_v4() PRIMARY KEY,
  date       DATE      NOT NULL DEFAULT CURRENT_DATE,
  type       TEXT      NOT NULL CHECK (type IN ('Pemasukan', 'Pengeluaran')),
  amount     NUMERIC   NOT NULL CHECK (amount > 0),
  category   TEXT      NOT NULL,
  notes      TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW())
);


-- 2. TABEL ENVELOPES (AMPLOP)
-- ============================================
CREATE TABLE IF NOT EXISTS public.envelopes (
  id                    UUID    DEFAULT uuid_generate_v4() PRIMARY KEY,
  name                  TEXT    NOT NULL UNIQUE,
  allocation_percentage NUMERIC NOT NULL CHECK (allocation_percentage >= 0 AND allocation_percentage <= 100),
  created_at            TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW())
);

-- Data default amplop
INSERT INTO public.envelopes (name, allocation_percentage)
  VALUES
    ('Dana Darurat',       20),
    ('Operasional',        40),
    ('Pajak & Biaya Admin',20),
    ('Self-Reward',        20)
  ON CONFLICT (name) DO NOTHING;


-- 3. TABEL PENDING INCOMES (PIUTANG KLIEN)
-- ============================================
CREATE TABLE IF NOT EXISTS public.pending_incomes (
  id          UUID    DEFAULT uuid_generate_v4() PRIMARY KEY,
  client_name TEXT    NOT NULL,
  amount      NUMERIC NOT NULL CHECK (amount > 0),
  due_date    DATE    NOT NULL,
  status      TEXT    NOT NULL CHECK (status IN ('Pending', 'Cair')),
  created_at  TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW())
);


-- 4. DATABASE FUNCTION — ATOMIK PENCAIRAN FAKTUR
-- ============================================
CREATE OR REPLACE FUNCTION mark_income_paid(
  p_income_id       UUID,
  p_client_name     TEXT,
  p_amount          NUMERIC,
  p_due_date        DATE,
  p_tax_percentage  NUMERIC DEFAULT 0
)
RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
  UPDATE public.pending_incomes
    SET status = 'Cair'
    WHERE id = p_income_id;

  INSERT INTO public.transactions (date, type, amount, category, notes)
    VALUES (
      p_due_date,
      'Pemasukan',
      p_amount,
      'Pencairan Faktur',
      'Dari: ' || p_client_name
    );

  IF p_tax_percentage > 0 THEN
    INSERT INTO public.transactions (date, type, amount, category, notes)
      VALUES (
        p_due_date,
        'Pengeluaran',
        p_amount * (p_tax_percentage / 100),
        'Pajak & Biaya Admin',
        'Pemotongan pajak ' || p_tax_percentage || '% faktur ' || p_client_name
      );
  END IF;
END;
$$;


-- 5. ROW LEVEL SECURITY
-- ============================================
ALTER TABLE public.transactions    ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.envelopes       ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.pending_incomes ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_only" ON public.transactions
  FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "service_role_only" ON public.envelopes
  FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "service_role_only" ON public.pending_incomes
  FOR ALL USING (auth.role() = 'service_role');