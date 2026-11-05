import json

notebook = {
    "cells": [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# **TUGAS ANALITIK TEKS / PEMROSESAN TEKS**\n",
                "## **Perhitungan Manual & Komputasi TF-IDF pada 5 Data Review (5 - 6 Kata)**\n",
                "\n",
                "---\n",
                "**Materi:** Pertemuan 8 - TF-IDF (Term Frequency - Inverse Document Frequency)  \n",
                "**Instruksi:**\n",
                "1. Menggunakan 5 data review dengan panjang kalimat masing-masing 5 - 6 kata (tanda baca & emoticon dihapus).\n",
                "2. Memilih 5 kata target yang dihitung TF-IDF nya.\n",
                "3. Tampilkan kalimatnya terlebih dahulu, kemudian lakukan perhitungan terperinci."
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "### **1. Daftar 5 Kalimat Review (Panjang 5 - 6 Kata)**\n",
                "\n",
                "| Dokumen | Kalimat Review Bersih (*Tokenized*) | Panjang Kata |\n",
                "| :---: | :--- | :---: |\n",
                "| **D1** | `pengiriman sangat cepat barang bagus` | 5 kata |\n",
                "| **D2** | `proses pengiriman aman packing rapi` | 5 kata |\n",
                "| **D3** | `respon penjual cepat produk mantap` | 5 kata |\n",
                "| **D4** | `kualitas produk ini sangat bagus sekali` | 6 kata |\n",
                "| **D5** | `harga murah produk ini cukup bagus` | 6 kata |\n",
                "\n",
                "*Total Dokumen ($N$) = 5*"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "### **2. Rumus Acuan Sesuai Slide Materi Perkuliahan**\n",
                "\n",
                "1. **Term Frequency (TF):**\n",
                "   $$\\text{TF}(t, d) = \\frac{\\text{Jumlah kemunculan kata } t \\text{ dalam dokumen } d}{\\text{Total kata dalam dokumen } d}$$\n",
                "\n",
                "2. **Inverse Document Frequency (IDF):**\n",
                "   $$\\text{IDF}(t, D) = \\log_{10} \\left( \\frac{N}{\\text{DF}} \\right)$$\n",
                "   *(Menggunakan logaritma basis 10 sesuai contoh pada slide: $\\log_{10}(1.5) = 0.176$ dan $\\log_{10}(3) = 0.477$).*\n",
                "\n",
                "3. **TF-IDF:**\n",
                "   $$\\text{TF-IDF} = \\text{TF} \\times \\text{IDF}$$"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "### **3. Perhitungan Document Frequency (DF) & IDF (N = 5)**\n",
                "\n",
                "1. **`pengiriman`**: Muncul di **D1, D2** $\\rightarrow$ $\\text{DF} = 2$  \n",
                "   $$\\text{IDF} = \\log_{10}\\left(\\frac{5}{2}\\right) = \\log_{10}(2.5) \\approx \\mathbf{0.398}$$\n",
                "\n",
                "2. **`packing`**: Muncul di **D2** saja $\\rightarrow$ $\\text{DF} = 1$ *(Kata dari D2 agar beda dari D1)*  \n",
                "   $$\\text{IDF} = \\log_{10}\\left(\\frac{5}{1}\\right) = \\log_{10}(5) \\approx \\mathbf{0.699}$$\n",
                "\n",
                "3. **`bagus`**: Muncul di **D1, D4, D5** $\\rightarrow$ $\\text{DF} = 3$  \n",
                "   $$\\text{IDF} = \\log_{10}\\left(\\frac{5}{3}\\right) = \\log_{10}(1.667) \\approx \\mathbf{0.222}$$\n",
                "\n",
                "4. **`cepat`**: Muncul di **D1, D3** $\\rightarrow$ $\\text{DF} = 2$  \n",
                "   $$\\text{IDF} = \\log_{10}\\left(\\frac{5}{2}\\right) = \\log_{10}(2.5) \\approx \\mathbf{0.398}$$\n",
                "\n",
                "5. **`produk`**: Muncul di **D3, D4, D5** $\\rightarrow$ $\\text{DF} = 3$  \n",
                "   $$\\text{IDF} = \\log_{10}\\left(\\frac{5}{3}\\right) = \\log_{10}(1.667) \\approx \\mathbf{0.222}$$"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "### **4. Perhitungan Spesifik (Kalimat Terlebih Dahulu, Lalu Hitungan)**\n",
                "\n",
                "#### **a. `pengiriman D1 =`**\n",
                "- **Kalimat D1:** `\"pengiriman sangat cepat barang bagus\"` *(5 kata)*\n",
                "- $\\text{TF}(\\text{\"pengiriman\"}, D1) = \\frac{1}{5} = \\mathbf{0.20}$\n",
                "- $\\text{IDF}(\\text{\"pengiriman\"}) = \\mathbf{0.398}$\n",
                "- **$\\text{TF-IDF} = 0.20 \\times 0.398 = \\mathbf{0.0796} \\approx \\mathbf{0.080}$**\n",
                "\n",
                "#### **b. `packing D2 =`** *(Kata dari D2 agar tidak sama dengan D1)*\n",
                "- **Kalimat D2:** `\"proses pengiriman aman packing rapi\"` *(5 kata)*\n",
                "- $\\text{TF}(\\text{\"packing\"}, D2) = \\frac{1}{5} = \\mathbf{0.20}$\n",
                "- $\\text{IDF}(\\text{\"packing\"}) = \\mathbf{0.699}$\n",
                "- **$\\text{TF-IDF} = 0.20 \\times 0.699 = \\mathbf{0.1398} \\approx \\mathbf{0.140}$**\n",
                "\n",
                "#### **c. `bagus D1 =`**\n",
                "- **Kalimat D1:** `\"pengiriman sangat cepat barang bagus\"` *(5 kata)*\n",
                "- $\\text{TF}(\\text{\"bagus\"}, D1) = \\frac{1}{5} = \\mathbf{0.20}$\n",
                "- $\\text{IDF}(\\text{\"bagus\"}) = \\mathbf{0.222}$\n",
                "- **$\\text{TF-IDF} = 0.20 \\times 0.222 = \\mathbf{0.0444} \\approx \\mathbf{0.044}$**\n",
                "\n",
                "#### **d. `CEPAT D3 =`**\n",
                "- **Kalimat D3:** `\"respon penjual cepat produk mantap\"` *(5 kata)*\n",
                "- $\\text{TF}(\\text{\"cepat\"}, D3) = \\frac{1}{5} = \\mathbf{0.20}$\n",
                "- $\\text{IDF}(\\text{\"cepat\"}) = \\mathbf{0.398}$\n",
                "- **$\\text{TF-IDF} = 0.20 \\times 0.398 = \\mathbf{0.0796} \\approx \\mathbf{0.080}$**\n",
                "\n",
                "#### **e. `produk D4 =`** *(Kata ke-5)*\n",
                "- **Kalimat D4:** `\"kualitas produk ini sangat bagus sekali\"` *(6 kata)*\n",
                "- $\\text{TF}(\\text{\"produk\"}, D4) = \\frac{1}{6} \\approx \\mathbf{0.167}$\n",
                "- $\\text{IDF}(\\text{\"produk\"}) = \\mathbf{0.222}$\n",
                "- **$\\text{TF-IDF} = 0.167 \\times 0.222 = \\mathbf{0.0370}$**"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "import math\n",
                "import pandas as pd\n",
                "\n",
                "corpus = {\n",
                "    \"D1\": \"pengiriman sangat cepat barang bagus\",\n",
                "    \"D2\": \"proses pengiriman aman packing rapi\",\n",
                "    \"D3\": \"respon penjual cepat produk mantap\",\n",
                "    \"D4\": \"kualitas produk ini sangat bagus sekali\",\n",
                "    \"D5\": \"harga murah produk ini cukup bagus\"\n",
                "}\n",
                "\n",
                "target_words = [\"pengiriman\", \"packing\", \"bagus\", \"cepat\", \"produk\"]\n",
                "N = len(corpus)\n",
                "\n",
                "doc_tokens = {k: v.split() for k, v in corpus.items()}\n",
                "doc_lengths = {k: len(v) for k, v in doc_tokens.items()}\n",
                "\n",
                "df_dict = {}\n",
                "idf_dict = {}\n",
                "for w in target_words:\n",
                "    docs_with_w = [d for d, tokens in doc_tokens.items() if w in tokens]\n",
                "    df_dict[w] = len(docs_with_w)\n",
                "    idf_dict[w] = math.log10(N / len(docs_with_w))\n",
                "\n",
                "tfidf_data = {\n",
                "    \"Kata\": target_words,\n",
                "    \"DF\": [df_dict[w] for w in target_words],\n",
                "    \"IDF\": [round(idf_dict[w], 3) for w in target_words]\n",
                "}\n",
                "for d in corpus:\n",
                "    tfidf_data[d] = [round((doc_tokens[d].count(w) / doc_lengths[d]) * idf_dict[w], 4) for w in target_words]\n",
                "\n",
                "df_matrix = pd.DataFrame(tfidf_data)\n",
                "display(df_matrix)"
            ]
        }
    ],
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python",
            "version": "3.12.0"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 4
}

with open("Tugas_TFIDF_Pertemuan_8.ipynb", "w", encoding="utf-8") as f:
    json.dump(notebook, f, indent=2, ensure_ascii=False)

print("Notebook 5-6 words generated successfully!")
