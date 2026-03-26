import streamlit as st
from utils.calculations import calculate_runway

def render_purchase_simulator(transactions_data, envelopes_data):
    st.subheader("🛒 Purchase Simulator")
    
    current_balance, avg_daily_expense, current_runway_days = calculate_runway(transactions_data)
    
    with st.expander("Simulasikan Pembelian Barang Non-Esensial", expanded=False):
        st.markdown("Mekanisme mitigasi FOMO. Cek dampaknya sebelum *Checkout*!")
        col1, col2 = st.columns(2)
        with col1:
            item_name = st.text_input("Nama Barang Idaman")
        with col2:
            item_price = st.number_input("Harga Barang (Rp)", min_value=0.0, step=50000.0, format="%.0f")
            
        if item_name and item_price > 0:
            st.markdown("---")
            st.markdown(f"#### Dampak Jika Membeli **{item_name}**")
            
            # Hitung saldo baru
            new_balance = current_balance - item_price
            
            # Dampak pada Runway Health
            if avg_daily_expense > 0:
                new_runway_days = new_balance / avg_daily_expense
            else:
                new_runway_days = 999.0 if new_balance > 0 else 0.0
                
            runway_diff = current_runway_days - new_runway_days
            
            col_metric1, col_metric2 = st.columns(2)
            # Batasi perbedaan hanya jika tidak 999
            if current_runway_days < 999:
                col_metric1.metric("Runway Lama", f"{current_runway_days:.0f} Hari")
                col_metric2.metric("Sisa Runway Baru", f"{new_runway_days:.0f} Hari", f"-{runway_diff:.0f} Hari", delta_color="inverse")
            else:
                col_metric1.metric("Runway Saat Ini", "Tak Terhingga")
                col_metric2.metric("Sisa Runway Baru", f"{new_runway_days:.0f} Hari" if new_runway_days < 999 else "Tak Terhingga")
            
            # Logika Dampak pada Virtual Envelopes
            self_reward_pct = 0
            important_envs = []
            
            for env in envelopes_data:
                env_name_lower = env['name'].lower()
                if "reward" in env_name_lower or "keinginan" in env_name_lower:
                    self_reward_pct = float(env['allocation_percentage'])
                else:
                    important_envs.append((env['name'], float(env['allocation_percentage'])))
            
            self_reward_budget = current_balance * (self_reward_pct / 100.0)
            
            st.markdown("##### 🔍 Pengecekan Amplop Self-Reward")
            if self_reward_budget >= item_price:
                st.success(f"✅ **Beli Saja!** Saldo Amplop *Self-Reward* Anda sangat cukup (Rp {self_reward_budget:,.0f}). Sisa setelah pembelian: Rp {(self_reward_budget - item_price):,.0f}.")
            else:
                shortfall = item_price - self_reward_budget
                st.error(f"❌ **TERLALU MAHAL!** Amplop Self-Reward Anda kurang Rp {shortfall:,.0f}.")
                st.warning("⚠️ Membeli barang ini akan **TERPAKSA** menyedot jatah dari Amplop Penting Anda:")
                
                # Simulasi penyedotan dari amplop lain berdasarkan proporsi mereka
                total_important_pct = sum([e[1] for e in important_envs])
                if total_important_pct == 0: total_important_pct = 1 # Hindari division by zero
                
                for env_name, env_pct in important_envs:
                    hit = shortfall * (env_pct / total_important_pct)
                    if hit > 0:
                        st.markdown(f"- 💸 **{env_name}** akan berkurang sebesar: **Rp {hit:,.0f}**")
