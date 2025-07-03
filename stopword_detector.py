#!/usr/bin/env python3
"""
Script untuk mendeteksi apakah semua kata dalam file CSV adalah stopword.
Menganalisis kata-kata berdasarkan karakteristik umum stopword.
"""

import pandas as pd
import re
from collections import Counter
import nltk
from nltk.corpus import stopwords
import string

# Download NLTK stopwords jika belum ada
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class StopwordDetector:
    def __init__(self, csv_file):
        self.csv_file = csv_file
        self.df = None
        self.all_words = []
        self.analysis_results = {}
        
        # Daftar stopword dari NLTK untuk perbandingan
        self.english_stopwords = set(stopwords.words('english'))
        
        # Karakteristik umum stopword
        self.common_stopword_patterns = {
            'pronouns': ['i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
                        'my', 'your', 'his', 'her', 'its', 'our', 'their', 'mine', 'yours', 'hers', 'ours', 'theirs',
                        'myself', 'yourself', 'himself', 'herself', 'itself', 'ourselves', 'yourselves', 'themselves',
                        'aku', 'kamu', 'dia', 'kita', 'mereka', 'saya', 'anda'],
            
            'articles': ['a', 'an', 'the'],
            
            'prepositions': ['in', 'on', 'at', 'by', 'for', 'with', 'to', 'from', 'of', 'about', 'into', 'through',
                           'during', 'before', 'after', 'above', 'below', 'up', 'down', 'out', 'off', 'over', 'under',
                           'di', 'ke', 'dari', 'untuk', 'dengan', 'oleh', 'pada', 'dalam', 'antara'],
            
            'conjunctions': ['and', 'or', 'but', 'so', 'yet', 'for', 'nor', 'because', 'since', 'although', 'though',
                           'while', 'if', 'unless', 'until', 'when', 'where', 'why', 'how',
                           'dan', 'atau', 'tetapi', 'karena', 'jika', 'ketika', 'dimana', 'mengapa', 'bagaimana'],
            
            'auxiliary_verbs': ['is', 'am', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having',
                              'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can',
                              'adalah', 'akan', 'sudah', 'sedang', 'bisa', 'harus', 'boleh'],
            
            'determiners': ['this', 'that', 'these', 'those', 'some', 'any', 'all', 'every', 'each', 'either', 'neither',
                          'much', 'many', 'few', 'little', 'more', 'most', 'less', 'least',
                          'ini', 'itu', 'semua', 'setiap', 'beberapa', 'banyak', 'sedikit', 'lebih', 'paling'],
            
            'question_words': ['what', 'who', 'when', 'where', 'why', 'how', 'which', 'whose',
                             'apa', 'siapa', 'kapan', 'dimana', 'mengapa', 'bagaimana', 'yang mana'],
            
            'negations': ['not', 'no', 'never', 'nothing', 'nobody', 'nowhere', 'neither', 'none',
                        'tidak', 'bukan', 'jangan', 'belum', 'tak'],
            
            'adverbs': ['very', 'quite', 'rather', 'too', 'so', 'just', 'only', 'even', 'still', 'already', 'yet',
                      'again', 'once', 'twice', 'always', 'usually', 'often', 'sometimes', 'rarely', 'never',
                      'here', 'there', 'everywhere', 'somewhere', 'anywhere', 'nowhere',
                      'now', 'then', 'today', 'yesterday', 'tomorrow', 'soon', 'later',
                      'sangat', 'hanya', 'juga', 'masih', 'sudah', 'lagi', 'selalu', 'sering', 'kadang',
                      'disini', 'disana', 'sekarang', 'kemarin', 'besok', 'nanti'],
            
            'contractions': ["n't", "'ll", "'re", "'ve", "'d", "'s", "'m"],
            
            'interjections': ['oh', 'ah', 'eh', 'um', 'uh', 'hmm', 'wow', 'hey', 'hi', 'hello', 'bye', 'yes', 'no',
                            'aduh', 'wah', 'eh', 'ya', 'iya', 'tidak', 'halo', 'hai'],
            
            'slang_informal': ['lol', 'omg', 'wtf', 'btw', 'fyi', 'asap', 'aka', 'etc', 'lmao', 'rofl',
                             'wkwk', 'haha', 'hehe', 'hihi', 'gw', 'gue', 'lu', 'lo', 'bro', 'sis']
        }
    
    def load_data(self):
        """Load CSV file dan ekstrak semua kata"""
        try:
            self.df = pd.read_csv(self.csv_file)
            print(f"✓ File berhasil dimuat: {len(self.df)} baris")
            print(f"✓ Kolom: {list(self.df.columns)}")
            
            # Ekstrak semua kata dari semua kolom
            for column in self.df.columns:
                words = self.df[column].dropna().astype(str).tolist()
                self.all_words.extend([word.strip().lower() for word in words if word.strip() and word.strip() != 'nan'])
            
            # Hapus duplikat dan kata kosong
            self.all_words = list(set([word for word in self.all_words if word and len(word) > 0]))
            print(f"✓ Total kata unik: {len(self.all_words)}")
            
        except Exception as e:
            print(f"✗ Error loading file: {e}")
            return False
        return True
    
    def analyze_word_characteristics(self):
        """Analisis karakteristik kata-kata"""
        results = {
            'total_words': len(self.all_words),
            'word_length_stats': {},
            'pattern_matches': {},
            'nltk_stopword_matches': 0,
            'non_stopword_candidates': [],
            'suspicious_words': []
        }
        
        # Statistik panjang kata
        word_lengths = [len(word) for word in self.all_words]
        results['word_length_stats'] = {
            'min': min(word_lengths),
            'max': max(word_lengths),
            'avg': sum(word_lengths) / len(word_lengths),
            'distribution': Counter(word_lengths)
        }
        
        # Cek kecocokan dengan pattern stopword
        for pattern_name, pattern_words in self.common_stopword_patterns.items():
            matches = [word for word in self.all_words if word in [p.lower() for p in pattern_words]]
            results['pattern_matches'][pattern_name] = {
                'count': len(matches),
                'words': matches[:10]  # Tampilkan 10 contoh
            }
        
        # Cek kecocokan dengan NLTK English stopwords
        nltk_matches = [word for word in self.all_words if word in self.english_stopwords]
        results['nltk_stopword_matches'] = len(nltk_matches)
        
        # Identifikasi kata yang mungkin bukan stopword
        all_pattern_words = set()
        for pattern_words in self.common_stopword_patterns.values():
            all_pattern_words.update([p.lower() for p in pattern_words])
        
        potential_non_stopwords = []
        for word in self.all_words:
            if (word not in self.english_stopwords and 
                word not in all_pattern_words and
                len(word) > 3 and
                not self.is_likely_stopword(word)):
                potential_non_stopwords.append(word)
        
        results['non_stopword_candidates'] = potential_non_stopwords[:20]  # Top 20
        
        # Identifikasi kata yang mencurigakan (mungkin bukan stopword)
        suspicious = []
        for word in self.all_words:
            if (len(word) > 6 or  # Kata panjang
                word.isdigit() or  # Angka
                any(char in string.punctuation for char in word) or  # Mengandung tanda baca
                word.isupper()):  # Semua huruf kapital
                suspicious.append(word)
        
        results['suspicious_words'] = suspicious[:20]
        
        self.analysis_results = results
        return results
    
    def is_likely_stopword(self, word):
        """Cek apakah kata kemungkinan adalah stopword berdasarkan karakteristik"""
        # Kata sangat pendek (1-2 karakter) biasanya stopword
        if len(word) <= 2:
            return True
        
        # Kata yang umum dalam bahasa Indonesia
        indonesian_common = ['yang', 'dan', 'ini', 'itu', 'untuk', 'dengan', 'dari', 'pada', 'dalam', 'oleh',
                           'akan', 'sudah', 'telah', 'sedang', 'masih', 'belum', 'tidak', 'bukan', 'jangan',
                           'ada', 'semua', 'setiap', 'beberapa', 'banyak', 'sedikit', 'lebih', 'paling',
                           'sangat', 'hanya', 'juga', 'lagi', 'selalu', 'sering', 'kadang', 'pernah']
        
        if word in indonesian_common:
            return True
        
        # Kata yang berakhiran umum stopword
        stopword_suffixes = ['nya', 'lah', 'kah', 'tah', 'pun']
        if any(word.endswith(suffix) for suffix in stopword_suffixes):
            return True
        
        return False
    
    def identify_non_stopwords(self):
        """Identifikasi kata-kata yang kemungkinan bukan stopword dengan kriteria yang lebih ketat"""
        non_stopwords = []

        # Kumpulkan semua kata yang dikenal sebagai stopword
        all_known_stopwords = set()

        # Tambahkan NLTK English stopwords
        all_known_stopwords.update(self.english_stopwords)

        # Tambahkan pattern stopwords
        for pattern_words in self.common_stopword_patterns.values():
            all_known_stopwords.update([p.lower() for p in pattern_words])

        # Daftar kata Indonesia yang umum sebagai stopword
        indonesian_stopwords = {
            'yang', 'dan', 'ini', 'itu', 'untuk', 'dengan', 'dari', 'pada', 'dalam', 'oleh',
            'akan', 'sudah', 'telah', 'sedang', 'masih', 'belum', 'tidak', 'bukan', 'jangan',
            'ada', 'semua', 'setiap', 'beberapa', 'banyak', 'sedikit', 'lebih', 'paling',
            'sangat', 'hanya', 'juga', 'lagi', 'selalu', 'sering', 'kadang', 'pernah',
            'aku', 'kamu', 'dia', 'kita', 'mereka', 'saya', 'anda', 'kalian',
            'dimana', 'kemana', 'darimana', 'bagaimana', 'mengapa', 'kenapa', 'kapan', 'siapa',
            'apa', 'mana', 'bila', 'jika', 'kalau', 'ketika', 'saat', 'waktu',
            'karena', 'sebab', 'akibat', 'hingga', 'sampai', 'setelah', 'sesudah', 'sebelum',
            'antara', 'diantara', 'sekitar', 'dekat', 'jauh', 'atas', 'bawah', 'depan', 'belakang',
            'kiri', 'kanan', 'tengah', 'luar', 'dalam', 'luas', 'sempit',
            'besar', 'kecil', 'panjang', 'pendek', 'tinggi', 'rendah', 'tebal', 'tipis',
            'berat', 'ringan', 'keras', 'lunak', 'kasar', 'halus', 'panas', 'dingin',
            'hangat', 'sejuk', 'basah', 'kering', 'bersih', 'kotor', 'baru', 'lama',
            'muda', 'tua', 'cepat', 'lambat', 'mudah', 'sulit', 'gampang', 'susah',
            'baik', 'buruk', 'bagus', 'jelek', 'cantik', 'indah', 'senang', 'sedih',
            'marah', 'takut', 'berani', 'sayang', 'cinta', 'benci'
        }
        all_known_stopwords.update(indonesian_stopwords)

        # Kata-kata slang dan informal yang umum
        slang_words = {
            'gw', 'gue', 'lu', 'lo', 'elu', 'w', 'u', 'km', 'sy', 'dy', 'mrk', 'kt', 'kmi',
            'yg', 'dgn', 'dr', 'utk', 'pd', 'dlm', 'olh', 'akn', 'sdh', 'sdg', 'msh', 'blm',
            'tdk', 'bkn', 'jgn', 'smu', 'bnyk', 'sdkt', 'sgt', 'hny', 'jg', 'lg', 'sll',
            'skrg', 'ntr', 'kmrn', 'bsk', 'hr', 'gmn', 'bgmn', 'dmn', 'kmn', 'drmn',
            'spa', 'sapa', 'ap', 'apa', 'mn', 'kpn', 'knp', 'krn', 'jk', 'ktk', 'saat',
            'wkt', 'di', 'ke', 'dari', 'untuk', 'dengan', 'pada', 'dalam', 'oleh',
            'udah', 'udeh', 'belom', 'blom', 'gitu', 'gini', 'banget', 'bgt', 'kayak', 'kaya',
            'kok', 'sih', 'deh', 'dong', 'lah', 'kah', 'tuh', 'nih', 'yah', 'wah', 'nah',
            'kan', 'ya', 'iya', 'yup', 'yep', 'oke', 'ok', 'okay'
        }
        all_known_stopwords.update(slang_words)

        # Partikel dan kata sambung
        particles = {
            'nya', 'mu', 'ku', 'pun', 'lah', 'kah', 'tah', 'deh', 'dong', 'sih', 'kok',
            'yah', 'wah', 'nah', 'kan', 'tuh', 'nih'
        }
        all_known_stopwords.update(particles)

        # Interjeksi dan ekspresi
        interjections = {
            'oh', 'ah', 'eh', 'uh', 'um', 'hmm', 'hm', 'em', 'ih', 'aduh', 'astaga',
            'alamak', 'waduh', 'duh', 'owh', 'owwh', 'owwwh', 'oooh', 'aaah', 'eeeh',
            'iiih', 'uuuh', 'haah', 'haaah', 'huft', 'hufh', 'hufft'
        }
        all_known_stopwords.update(interjections)

        # Cek setiap kata
        for word in self.all_words:
            is_stopword = False

            # Skip jika kata kosong atau terlalu pendek
            if not word or len(word) < 1:
                continue

            # Cek apakah kata ada dalam daftar stopword yang dikenal
            if word.lower() in all_known_stopwords:
                is_stopword = True

            # Cek apakah kata berakhiran partikel
            elif any(word.endswith(suffix) for suffix in ['nya', 'lah', 'kah', 'tah', 'pun']):
                is_stopword = True

            # Cek apakah kata adalah singkatan umum
            elif word in ['brb', 'btw', 'cmiiw', 'fyi', 'imho', 'lol', 'omg', 'wtf', 'asap', 'aka', 'etc', 'lmao', 'rofl', 'ttyl', 'imo', 'tbh', 'nvm', 'idk', 'irl', 'dm', 'pm']:
                is_stopword = True

            # Cek apakah kata adalah variasi tawa
            elif word in ['haha', 'hahaha', 'hahahaha', 'hehe', 'hehehe', 'hihi', 'hoho', 'huhu', 'wakaka', 'wakakaka', 'kwkw', 'kwkwkw', 'kkkk', 'kkkkk', 'wkwk', 'wkwkwk', 'wkwkwkwk', 'xixixi', 'xixi']:
                is_stopword = True

            # Cek apakah kata adalah angka atau mengandung angka
            elif word.isdigit() or any(char.isdigit() for char in word):
                # Kecuali jika itu nama tempat atau hal spesifik
                if word not in ['b2', 'b3', 'ms', 'th', 't4', 'gr2', 'pa2', 'kt2', 'sm2']:
                    is_stopword = False  # Angka biasanya bukan stopword

            # Jika tidak memenuhi kriteria stopword, tambahkan ke daftar non-stopword
            if not is_stopword:
                non_stopwords.append(word)

        return sorted(list(set(non_stopwords)))

    def separate_non_stopwords(self, output_file='non_stopwords.csv'):
        """Pisahkan kata-kata yang bukan stopword ke file CSV terpisah"""
        non_stopwords = self.identify_non_stopwords()

        if not non_stopwords:
            print("✅ Semua kata teridentifikasi sebagai stopword!")
            return

        # Buat DataFrame untuk kata-kata yang bukan stopword
        non_stopword_rows = []

        # Cari baris yang mengandung kata-kata non-stopword
        for idx, row in self.df.iterrows():
            contains_non_stopword = False
            for col in self.df.columns:
                if pd.notna(row[col]) and str(row[col]).strip().lower() in [w.lower() for w in non_stopwords]:
                    contains_non_stopword = True
                    break

            if contains_non_stopword:
                non_stopword_rows.append(row)

        if non_stopword_rows:
            # Simpan ke file CSV
            non_stopword_df = pd.DataFrame(non_stopword_rows)
            non_stopword_df.to_csv(output_file, index=False)
            print(f"✅ {len(non_stopword_rows)} baris dengan kata non-stopword disimpan ke: {output_file}")

            # Hapus baris non-stopword dari file asli
            clean_df = self.df.drop(non_stopword_df.index)
            clean_file = self.csv_file.replace('.csv', '_cleaned.csv')
            clean_df.to_csv(clean_file, index=False)
            print(f"✅ File bersih (hanya stopword) disimpan ke: {clean_file}")

            return non_stopwords, len(non_stopword_rows)
        else:
            print("✅ Tidak ada baris yang mengandung kata non-stopword")
            return non_stopwords, 0

    def generate_report(self):
        """Generate laporan analisis"""
        if not self.analysis_results:
            print("✗ Belum ada hasil analisis. Jalankan analyze_word_characteristics() terlebih dahulu.")
            return

        results = self.analysis_results

        print("\n" + "="*60)
        print("LAPORAN ANALISIS STOPWORD")
        print("="*60)

        print(f"\n📊 STATISTIK UMUM:")
        print(f"   Total kata unik: {results['total_words']}")
        print(f"   Panjang kata minimum: {results['word_length_stats']['min']}")
        print(f"   Panjang kata maksimum: {results['word_length_stats']['max']}")
        print(f"   Rata-rata panjang kata: {results['word_length_stats']['avg']:.2f}")

        print(f"\n📈 DISTRIBUSI PANJANG KATA:")
        for length, count in sorted(results['word_length_stats']['distribution'].items()):
            percentage = (count / results['total_words']) * 100
            print(f"   {length} karakter: {count} kata ({percentage:.1f}%)")

        print(f"\n🎯 KECOCOKAN DENGAN PATTERN STOPWORD:")
        total_pattern_matches = 0
        for pattern_name, data in results['pattern_matches'].items():
            if data['count'] > 0:
                print(f"   {pattern_name.title()}: {data['count']} kata")
                if data['words']:
                    print(f"      Contoh: {', '.join(data['words'][:5])}")
                total_pattern_matches += data['count']

        print(f"\n🔍 KECOCOKAN DENGAN NLTK ENGLISH STOPWORDS:")
        print(f"   {results['nltk_stopword_matches']} kata cocok dengan NLTK stopwords")

        print(f"\n⚠️  KANDIDAT BUKAN STOPWORD:")
        if results['non_stopword_candidates']:
            print(f"   {len(results['non_stopword_candidates'])} kata berpotensi bukan stopword:")
            for word in results['non_stopword_candidates'][:10]:
                print(f"      - {word}")
        else:
            print("   Tidak ada kata yang teridentifikasi sebagai bukan stopword")

        print(f"\n🚨 KATA MENCURIGAKAN:")
        if results['suspicious_words']:
            print(f"   {len(results['suspicious_words'])} kata mencurigakan:")
            for word in results['suspicious_words'][:10]:
                print(f"      - {word}")
        else:
            print("   Tidak ada kata mencurigakan")

        # Kesimpulan
        print(f"\n🎯 KESIMPULAN:")
        stopword_percentage = ((total_pattern_matches + results['nltk_stopword_matches']) / results['total_words']) * 100

        if stopword_percentage >= 90:
            conclusion = "✅ SANGAT BAIK - Hampir semua kata adalah stopword"
        elif stopword_percentage >= 80:
            conclusion = "✅ BAIK - Sebagian besar kata adalah stopword"
        elif stopword_percentage >= 70:
            conclusion = "⚠️  CUKUP - Banyak kata adalah stopword, tapi ada beberapa yang perlu diperiksa"
        else:
            conclusion = "❌ KURANG - Banyak kata yang mungkin bukan stopword"

        print(f"   Persentase stopword: {stopword_percentage:.1f}%")
        print(f"   Status: {conclusion}")

        if results['non_stopword_candidates'] or results['suspicious_words']:
            print(f"\n💡 REKOMENDASI:")
            print(f"   - Periksa kata-kata dalam daftar 'kandidat bukan stopword'")
            print(f"   - Verifikasi kata-kata mencurigakan")
            print(f"   - Pertimbangkan untuk menghapus kata yang bukan stopword")

        # Jalankan pemisahan non-stopword
        print(f"\n🔄 MEMISAHKAN KATA NON-STOPWORD...")
        non_stopwords, moved_rows = self.separate_non_stopwords()

        if non_stopwords:
            print(f"\n📋 DAFTAR KATA NON-STOPWORD YANG DITEMUKAN ({len(non_stopwords)} kata):")
            for i, word in enumerate(non_stopwords[:20], 1):
                print(f"   {i:2d}. {word}")
            if len(non_stopwords) > 20:
                print(f"   ... dan {len(non_stopwords) - 20} kata lainnya")

        print(f"\n✅ PROSES SELESAI!")
        print(f"   - {moved_rows} baris dipindahkan ke file non_stopwords.csv")
        print(f"   - File bersih disimpan sebagai {self.csv_file.replace('.csv', '_cleaned.csv')}")

def main():
    detector = StopwordDetector('multilingual_stopwords_dict_only_revisi.csv')
    
    print("🔍 DETEKSI STOPWORD - ANALISIS FILE CSV")
    print("="*50)
    
    if detector.load_data():
        print("\n📊 Menganalisis karakteristik kata...")
        detector.analyze_word_characteristics()
        detector.generate_report()
    else:
        print("❌ Gagal memuat file CSV")

if __name__ == "__main__":
    main()
