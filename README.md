# Panduan Menjalankan Dashboard Streamlit dengan Conda

Berikut adalah langkah-langkah lengkap untuk menjalankan aplikasi **Streamlit** menggunakan **Conda environment**.

---

```bash
conda create --name main-ds python=3.9
conda activate main-ds
pip install -r requirements.txt
cd ecommerce-data-analysis/dashboard
pipenv install
pipenv shell
pip install -r requirements.txt
streamlit run dashboard.py
```
