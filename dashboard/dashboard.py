import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import locale
import geopandas as gpd
from folium.plugins import MarkerCluster
import plotly.express as px

# Load dataset
main_df = pd.read_csv("dashboard/main_data.csv")
locale.setlocale(locale.LC_TIME, "id_ID.UTF-8")

# Beginning
st.title("E-Commerce Data Analysis - Interactive Story")
st.markdown("""
    Dalam proyek ini, kita akan mengeksplorasi tiga pertanyaan bisnis yang penting tentang 
    **tren penjualan, pengaruh keterlambatan pengiriman terhadap kepuasan pelanggan**, dan 
    **sebaran geografis keterlambatan pengiriman di Brasil**.
    **Ayo mulai perjalanan interaktif ini!**
""")

st.markdown("---")

# Pertanyaan Bisnis 1
st.markdown("## 🤔 **Gimana sih Tren Penjualan di Sepanjang Tahun 2017?**")
st.markdown("""
    Pada tahun 2017, jumlah pesanan menunjukkan tren **meningkat sepanjang tahun**, 
    dengan puncaknya terjadi pada **bulan Desember**. Mari kita lihat lebih dekat bagaimana 
    tren penjualan berkembang setiap bulannya.
""")

main_df["order_delivered_customer_date"] = pd.to_datetime(main_df["order_delivered_customer_date"])
df_2017 = main_df[main_df["order_delivered_customer_date"].dt.year == 2017].copy()
df_2017["order_month"] = df_2017["order_delivered_customer_date"].dt.strftime("%B")
bulan_sorted = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", 
                "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
monthly_orders = df_2017["order_month"].value_counts().reindex(bulan_sorted, fill_value=0)
monthly_orders_df = pd.DataFrame({
    "Bulan": monthly_orders.index,
    "Jumlah Pesanan": monthly_orders.values
})
monthly_orders_df.set_index("Bulan", inplace=True)

# Visualisasi: Line Chart
st.markdown("#### Tren Jumlah Pesanan per Bulan, 2017")
st.line_chart(monthly_orders_df)

# Interpretasi
st.markdown("Lonjakan tertinggi tersebut bisa saja dipengaruhi oleh tren belanja akhir tahun dan strategi promosi. Meskipun terjadi peningkatan secara umum, terdapat beberapa fluktuasi seperti penurunan di bulan April dan September yang bisa dikaitkan dengan faktor musiman atau perubahan pola belanja pelanggan. Analisis lebih lanjut diperlukan untuk memahami penyebab fluktuasi ini dan bagaimana strategi bisnis dapat menyesuaikan diri.")
st.markdown("---")


# Pertanyaan Bisnis 2
st.markdown("""  
            ## 🔄 **Hmm, terus gimana ya Waktu Pengiriman bisa memengaruhi Kepuasan Pelanggan?**

Kita telah melihat bahwa tren jumlah pesanan **meningkat sepanjang tahun**, dengan **lonjakan signifikan pada bulan Desember**. Namun, ada pertanyaan yang lebih dalam:

💡 **Apakah semua pesanan tiba tepat waktu?**  
💡 **Bagaimana keterlambatan pengiriman mempengaruhi pengalaman pelanggan?**  

Selanjutnya, kita akan menganalisis apakah **keterlambatan pengiriman berdampak pada review pelanggan**. Apakah semakin lama keterlambatan, semakin buruk *review* yang diberikan pelanggan? Mari kita lihat! 👇
""")

# Visualisasi: Boxplot
st.markdown("#### Hubungan Keterlambatan Pengiriman & Review Score, 2017")
fig = px.box(main_df, 
             x="review_score", 
             y="shipping_delay_days", 
             color="review_score", 
             color_discrete_sequence=px.colors.qualitative.Set1,
             title="")
fig.update_layout(
    xaxis_title="Review Score",
    yaxis_title="Jumlah Hari Keterlambatan",
    boxmode="group"
)
st.plotly_chart(fig)
df_2017["delay_category"] = pd.cut(df_2017["shipping_delay_days"], 
                                   bins=[float('-inf'), 0, 2, 5, 10, float('inf')], 
                                   labels=["Tepat Waktu", "Terlambat 1-2 Hari", "Terlambat 3-5 Hari", "Terlambat 6-10 Hari", "Terlambat >10 Hari"])

delay_review_avg = df_2017.groupby("delay_category")["review_score"].mean().reset_index()
category_order = ["Tepat Waktu", "Terlambat 1-2 Hari", "Terlambat 3-5 Hari", "Terlambat 6-10 Hari", "Terlambat >10 Hari"]
delay_review_avg["delay_category"] = pd.Categorical(delay_review_avg["delay_category"], categories=category_order, ordered=True)
delay_review_avg = delay_review_avg.sort_values("delay_category")
delay_review_avg.set_index("delay_category", inplace=True)

# Visualisasi: Bar Chart
st.bar_chart(delay_review_avg)

# Pearson correlation
correlation = df_2017["shipping_delay_days"].corr(df_2017["review_score"])
st.metric(label="Korelasi Pearson", value=f"{correlation:.4f}")

# Interpretasi
st.markdown("Terdapat hubungan **negatif dan lemah** antara keterlambatan pengiriman dan review score (**Pearson = -0.1954**), yang berarti semakin lama keterlambatan, semakin rendah rating pelanggan, tetapi bukan satu-satunya faktor penentu. Oleh karena itu, mengurangi keterlambatan pengiriman saja tidak cukup. Perusahaan juga perlu meningkatkan layanan pelanggan dan memastikan kualitas produk untuk mempertahankan kepuasan pelanggan dan rating yang tinggi.  ")
st.markdown("---")


# Pertanyaan Bisnis 3
st.markdown("""  
## 🌎 **Lalu, Di Mana *sih* Keterlambatan Pengiriman Paling Sering Terjadi?**

Dari analisis sebelumnya, kita menemukan bahwa **keterlambatan pengiriman memang berpengaruh terhadap review pelanggan**, tetapi **bukan satu-satunya faktor penentu**. Selain itu, kita juga melihat bahwa **tidak semua pelanggan yang mengalami keterlambatan memberikan review buruk**, yang berarti ada faktor lain seperti **kualitas produk dan layanan pelanggan** yang turut berperan. Namun, sekarang muncul pertanyaan baru: 

***Di mana keterlambatan pengiriman paling sering terjadi?***  

Untuk menjawab ini, kita akan mengeksplorasi **peta sebaran keterlambatan pengiriman di berbagai state di Brasil**. Mari kita lanjutkan! 👇
""")

# Prepare geo data
state_delay = main_df.groupby("customer_state")["shipping_delay_days"].mean().reset_index()
brasil_map = gpd.read_file("https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson")
brasil_map = brasil_map.rename(columns={"sigla": "customer_state"}) 
brasil_map_merged = brasil_map.merge(state_delay, on="customer_state", how="left")
brasil_map_merged["centroid"] = brasil_map_merged.geometry.centroid
brasil_map_merged["ket"] = brasil_map_merged["shipping_delay_days"].apply(lambda x: f"Lebih cepat {abs(x):.1f} hari" if x < 0 else f"Terlambat {x:.1f} hari")

st.text("\n")

# Visualisasi: Choropleth Map
st.markdown("#### Rata-rata Keterlambatan Pengiriman di Brasil per State, 2017")
fig = px.choropleth(
    brasil_map_merged,
    geojson=brasil_map_merged.geometry,
    locations=brasil_map_merged.index,
    color="shipping_delay_days",
    hover_name="name",
    hover_data={"shipping_delay_days": False, "ket": True},
    color_continuous_scale="greens",
    title=""
)
fig.update_geos(fitbounds="locations", visible=False)
fig.update_traces(marker_line_color="white", marker_line_width=0.1)
fig.update_layout(
    margin={"r": 0, "t": 40, "l": 0, "b": 0},
    coloraxis_colorbar=dict(title="Hari Keterlambatan"),
    hovermode="closest"
)
st.plotly_chart(fig)

# Visualisasi: Number by dropdown
state_selected = st.selectbox("Pilih State", options=brasil_map_merged["name"].unique())
state_info = main_df[main_df["name"] == state_selected]
avg_delay = state_info["shipping_delay_days"].mean()*-1
num_customers = state_info["customer_id"].nunique()

col1, col2 = st.columns(2)
with col1:
    st.metric(label=f"Jumlah Pelanggan di {state_selected}", value=num_customers)
with col2:
    st.metric(label=f"Rata-rata Pesanan sampai Lebih Cepat", value=f"{avg_delay:.2f} hari")


# Interpretasi
st.markdown("Semua pesanan yang dikirim ke setiap State di Brasil pada tahun 2017 ternyata sampai ke pelanggan **lebih cepat dari estimasi**. Hal ini mungkin saja terjadi karena sistem estimasi pengiriman mungkin terlalu konservatif sehingga pesanan tiba lebih cepat dari yang diprediksi. Wilayah terpencil seperti Acre, Amazonas, dan Rondônia memiliki estimasi pengiriman yang berlebihan, sedangkan wilayah metropolitan seperti São Paulo (SP) dan Rio de Janeiro (RJ) memiliki estimasi yang lebih akurat. Perusahaan dapat menyesuaikan estimasi pengiriman agar lebih akurat, mengoptimalkan biaya logistik, dan memastikan pelanggan memiliki ekspektasi realistis terkait waktu pengiriman.  ")

# Ending
st.markdown("---")
st.markdown("#### **Terima Kasih telah Menjelajahi Analisis E-Commerce ini!**")
st.caption('Copyright by Bimo Ade Budiman Fikri - Laskar AI (c) 2025')
