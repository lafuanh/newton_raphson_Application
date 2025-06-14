import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from core_mechanic import newton_raphson, cost_function

# config pages
st.set_page_config(
    page_title="Optimasi Biaya Produksi",
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
        text-align: center;
        color: #1E88E5;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #424242;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stAlert {
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">Optimasi Biaya Produksi</h1>', unsafe_allow_html=True)
st.markdown("### Minimalkan biaya produksi menggunakan metode Newton-Raphson")

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
            optimal_Q, history, converged = newton_raphson(
                params, initial_guess, tolerance, max_iterations
            )

            if converged:
                st.success(f"Optimasi berhasil dalam {len(history)} iterasi!")
            else:
                st.warning(f"!! Iterasi maksimum tercapai ({max_iterations})")

            # Display
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

            col_b1 = st.columns(1)[0]
            # with col_b1:
            #     st.dataframe(breakdown_df.style.format({'Jumlah': 'Rp {:,.0f}', 'Persentase': '{:.1f}%'}))
            #
            # # Pie chart
            # fig_pie = go.Figure(data=[go.Pie(
            #     labels=['Material'],
            #     values=[material_cost],
            #     hole=.3
            # )])
            #
            # fig_pie.update_layout(
            #     height=250,
            #     margin=dict(t=0, b=0, l=0, r=0),
            #     showlegend=True
            # )
            # st.plotly_chart(fig_pie, use_container_width=True)

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
