import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from core_mechanic import newton_raphson, cost_function

# config pages
st.set_page_config(
    page_title="Optimasi Jumlah Produksi untuk Meminimalkan Biaya Total Produksi Menggunakan Metode Newton-Raphson",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS
st.markdown("""
    <style>
        .main-header {
            font-size: 3rem;
            font-weight: bold;
            text-align: left;
            color: #FFFFF;
            margin-bottom: 2rem;
        }
        .sub-header {
            font-size: 1.5rem;
            color: #525252;
            margin-bottom: 1rem;
        }
        .metric-card {
            background-color: transparent !important;
            padding: 0 !important;
            box-shadow: none !important;
        }
        .stAlert {
            margin-top: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

# Header and description
st.markdown('<h1 class="main-header">PROYEK MATA KULIAH METODE NUMERIK KELOMPOK 4</h1>', unsafe_allow_html=True)
st.markdown("### Optimasi Jumlah Produksi untuk Meminimalkan Biaya Total Produksi Menggunakan Metode Newton-Raphson")

# Sidebar for user input
with st.sidebar:
    st.header("Parameter Fungsi Biaya")

    st.subheader("Biaya Material")
    a = st.number_input("Percepatan Naiknya Biaya Material (a)", value=0.1, step=0.01)
    b = st.number_input("Biaya Per Unit Material (b)", value=60.0, step=1.0)
    c = st.number_input("Biaya Tetap Material (c)", value=60000.0, step=100.0)

    st.subheader("Ekonomi Skala")
    d = st.number_input("Pengaruh Ekonomi Skala (d)", value=10000.0, step=1000.0)
    f = st.number_input("Kecepatan Penurunan Biaya (f)", value=0.01, step=0.0001)

    st.header("🔧 Parameter Algoritma")
    initial_guess = st.number_input("Kuantitas Produksi Awal", value=9000.0, min_value=1.0, step=10.0)
    tolerance = st.number_input("Toleransi Kesalahan", value=0.000001, format="%.6f", step=0.000001)
    max_iterations = st.number_input("Iterasi Maksimum", value=100, min_value=10, step=10)

# Column for result display
col1, col2 = st.columns([2, 1])

with col1:
    st.header("Hasil Optimasi")
    params = {
        'a': a,
        'b': b,
        'c': c,
        'd': d,
        'f': f
    }


    if st.button("Optimalkan Produksi", type="primary", use_container_width=True):
        with st.spinner("Menjalankan optimasi Newton-Raphson..."):
            # Run the Newton-Raphson optimization
            optimal_Q, history, converged = newton_raphson(
                params, initial_guess, tolerance, max_iterations
            )

            # Show result of optimization
            if converged:
                st.success(f"Optimasi berhasil dalam {len(history)} iterasi!")
            else:
                st.warning(f"!! Iterasi maksimum tercapai ({max_iterations})")

            # Display the iteration history in a table
            st.subheader("Rincian Iterasi Optimasi")
            iteration_df = pd.DataFrame(history)
            iteration_df['TC\'(Q)'] = iteration_df['TC\'(Q)'].apply(lambda x: f"{x:.15f}")  # Precision for derivatives
            iteration_df['TC\'\'(Q)'] = iteration_df['TC\'\'(Q)'].apply(lambda x: f"{x:.15f}")
            iteration_df['Galat'] = iteration_df['Galat'].apply(lambda x: f"{x:.15f}")  # Precision for error

            # Display the table with iteration history
            st.dataframe(iteration_df, use_container_width=True)

            # Display results for optimal values
            col_m1, col_m2, col_m3 = st.columns(3)

            with col_m1:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("Kuantitas Produksi Optimal", f"{optimal_Q:.2f} unit")
                st.markdown('</div>', unsafe_allow_html=True)

            with col_m2:
                min_cost = cost_function(optimal_Q, params)
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("Total Biaya Minimum", f"Rp {min_cost:,.0f}")
                st.markdown('</div>', unsafe_allow_html=True)

            with col_m3:
                unit_cost = min_cost / optimal_Q if optimal_Q > 0 else 0
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("Biaya per Unit", f"Rp {unit_cost:,.0f}")
                st.markdown('</div>', unsafe_allow_html=True)

            # Show cost breakdown
            st.subheader("Rincian Biaya pada Kuantitas Optimal")
            material_cost = a * optimal_Q ** 2 + b * optimal_Q + c
            breakdown_df = pd.DataFrame({
                'Komponen Biaya': ['Material', 'Total'],
                'Jumlah': [material_cost, min_cost],
                'Persentase': [
                    material_cost / min_cost * 100,
                    100
                ]
            })
            st.dataframe(breakdown_df.style.format({'Jumlah': 'Rp {:,.0f}', 'Persentase': '{:.1f}%'}))

            # Show the Iteration Table (Optimized)
            iteration_df = pd.DataFrame(history, columns=['Iterasi', 'Qn', 'TC\'(Q)', 'TC\'\'(Q)', 'Galat', 'Ket'])
            iteration_df['TC\'(Q)'] = iteration_df['TC\'(Q)'].apply(lambda x: f'Rp {x:,.0f}')  # Format as currency
            iteration_df['Galat'] = iteration_df['Galat'].apply(lambda x: f'{x:.5f}')
            iteration_df['Ket'] = iteration_df['Ket'].apply(lambda x: 'Memenuhi' if x == 'Memenuhi' else 'Tidak Memenuhi')



            # Generate Q range for plotting the total cost function
            Q_range = np.linspace(1, optimal_Q * 2, 100)  # Range of production quantities
            total_costs = [cost_function(Q, params) for Q in Q_range]

            # Plot the total cost graph
            fig_cost = go.Figure()
            fig_cost.add_trace(go.Scatter(
                x=Q_range,
                y=total_costs,
                mode='lines',
                name='Total Biaya',
                line=dict(color='blue', width=3)
            ))

            # Highlight the optimal Q point on the graph
            fig_cost.add_trace(go.Scatter(
                x=[optimal_Q],
                y=[min_cost],
                mode='markers',
                name='Titik Optimal',
                marker=dict(color='red', size=12, symbol='star')
            ))

            fig_cost.update_layout(
                title="Total Biaya vs Kuantitas Produksi",
                xaxis_title="Kuantitas Produksi (unit)",
                yaxis_title="Total Biaya (Rp)",
                hovermode='x unified',
                height=400,
                yaxis_tickformat=',.0f'
            )

            st.plotly_chart(fig_cost, use_container_width=True)

    # Guide Section
    st.markdown("### Panduan Penggunaan Aplikasi")
    st.markdown("""
    Aplikasi ini digunakan untuk melakukan **Optimasi Jumlah Produksi** dengan tujuan untuk **Meminimalkan Biaya Total Produksi** menggunakan **Metode Newton-Raphson**. 

    **Langkah-langkah Penggunaan:**
    1. Masukkan nilai parameter fungsi biaya pada sidebar:
        - **Percepatan Naiknya Biaya Material (a)**: Menggambarkan bagaimana biaya material berubah seiring dengan peningkatan jumlah produksi.
        - **Biaya Per Unit Material (b)**: Biaya tetap per unit material.
        - **Biaya Tetap Material (c)**: Biaya tetap untuk material yang tidak tergantung pada jumlah produksi.
        - **Pengaruh Ekonomi Skala (d)**: Menyatakan bagaimana biaya total berkurang seiring peningkatan jumlah produksi (pengaruh ekonomi skala).
        - **Kecepatan Penurunan Biaya (f)**: Mengatur seberapa cepat biaya menurun dengan meningkatnya jumlah produksi.

    2. Tentukan parameter **Algoritma**:
        - **Kuantitas Produksi Awal**: Nilai awal untuk jumlah produksi yang digunakan oleh algoritma.
        - **Toleransi Kesalahan**: Toleransi kesalahan untuk konvergensi algoritma.
        - **Iterasi Maksimum**: Jumlah iterasi maksimal yang akan dijalankan oleh algoritma untuk mencapai konvergensi.

    3. Klik tombol **Optimalkan Produksi** untuk menjalankan perhitungan optimasi.


    **Metode Newton-Raphson**:
    Metode ini digunakan untuk mencari titik minimum dari fungsi biaya dengan memperbarui estimasi kuantitas produksi berdasarkan turunan pertama dan kedua dari fungsi biaya. Algoritma ini akan terus memperbarui estimasi kuantitas produksi sampai perubahan antara iterasi lebih kecil dari nilai toleransi yang ditentukan.

    **Penulis:**
    Aplikasi ini dibuat oleh **KELOMPOK 4** yang beranggotakan:
    1. Tyto Rinandi       NIM 2304030142
    2. Rahmat Hidayat     NIM 2304030145
    3. Lutfi Adi Prakoso  NIM 2304030148
    4. Naufal Adyatma     NIM 2304030174

    Semoga aplikasi ini membantu dalam perhitungan optimasi biaya produksi!
    """)
