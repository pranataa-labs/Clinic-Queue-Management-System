import math
import sys

sys.stdout.reconfigure(encoding='utf-8')

# 5 Data Review Produk (Rentang 5 - 6 kata per kalimat)
# Tanda baca, emoticon sudah dibersihkan, huruf kecil (case folding)
corpus = {
    "D1": "pengiriman sangat cepat barang bagus",          # 5 kata
    "D2": "proses pengiriman aman packing rapi",           # 5 kata
    "D3": "respon penjual cepat produk mantap",            # 5 kata
    "D4": "kualitas produk ini sangat bagus sekali",       # 6 kata
    "D5": "harga murah produk ini cukup bagus"             # 6 kata
}

target_words = ["pengiriman", "packing", "bagus", "cepat", "produk"]
N = len(corpus)

doc_tokens = {k: v.split() for k, v in corpus.items()}
doc_lengths = {k: len(v) for k, v in doc_tokens.items()}

print("="*60)
print("1. DAFTAR KALIMAT REVIEW (5 - 6 KATA)")
print("="*60)
for d in corpus:
    print(f"[{d}] ({doc_lengths[d]} kata): \"{corpus[d]}\"")

print("\n" + "="*60)
print("2. PERHITUNGAN DF & IDF (N = 5 DOKUMEN)")
print("="*60)
df = {}
idf = {}
for w in target_words:
    docs = [d for d, tokens in doc_tokens.items() if w in tokens]
    df[w] = len(docs)
    val = math.log10(N / len(docs))
    idf[w] = val
    print(f"Kata '{w:<11}': Muncul di {docs} (DF = {len(docs)}) | IDF = log10({N}/{len(docs)}) = {val:.4f} (bulat: {val:.3f})")

print("\n" + "="*60)
print("3. PERHITUNGAN SPESIFIK (KALIMAT DULU, KEMUDIAN HITUNG)")
print("="*60)
tasks = [
    ("pengiriman", "D1"),
    ("packing", "D2"),
    ("bagus", "D1"),
    ("cepat", "D3"),
    ("produk", "D4")
]

for w, d in tasks:
    count = doc_tokens[d].count(w)
    tf = count / doc_lengths[d]
    tfidf = tf * idf[w]
    print(f">>> {w.upper()} ({d}):")
    print(f"    Kalimat {d} : \"{corpus[d]}\" (total {doc_lengths[d]} kata)")
    print(f"    TF         : {count}/{doc_lengths[d]} = {tf:.3f} (atau {round(tf, 2)})")
    print(f"    IDF        : log10({N}/{df[w]}) = {idf[w]:.3f}")
    print(f"    TF-IDF     : {round(tf, 2)} * {idf[w]:.3f} = {round(round(tf, 2) * round(idf[w], 3), 4)} (atau {tfidf:.4f})\n")

print("="*60)
print("4. TABEL MATRIKS TF-IDF")
print("="*60)
header = f"{'Kata':<12} | {'DF':<4} | {'IDF':<6} | " + " | ".join([f"{d:<8}" for d in corpus])
print(header)
print("-" * len(header))
for w in target_words:
    row = [f"{w:<12}", f"{df[w]:<4}", f"{idf[w]:.3f}"]
    for d in corpus:
        c = doc_tokens[d].count(w)
        score = (c / doc_lengths[d]) * idf[w]
        row.append(f"{score:.4f}  ")
    print(" | ".join(row))
