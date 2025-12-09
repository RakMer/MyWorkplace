#!/usr/bin/env python3
"""
Tüm akaryakıt firmalarının fiyat verilerini sırayla toplayan ana script
"""
import subprocess
import sys
from datetime import datetime

# Çalıştırılacak scriptler (sırayla)
SCRIPTS = [
    "Shell.py",
    "Lukoil.py", 
    "Opet.py",
    "PetrolOfisi.py",
    "Total.py",
    "TP.py"
]

def run_script(script_name):
    """Bir Python scriptini çalıştırır ve sonucu döndürür"""
    print(f"\n{'='*60}")
    print(f"🚀 {script_name} çalıştırılıyor...")
    print(f"{'='*60}")
    
    try:
        # Script'i çalıştır
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True,
            timeout=300  # 5 dakika timeout
        )
        
        # Çıktıyı göster
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
            
        # Başarı durumunu kontrol et
        if result.returncode == 0:
            print(f"✅ {script_name} başarıyla tamamlandı!")
            return True
        else:
            print(f"❌ {script_name} hata ile sonlandı! (Exit code: {result.returncode})")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏱️ {script_name} zaman aşımına uğradı (5 dakika)!")
        return False
    except Exception as e:
        print(f"❌ {script_name} çalıştırılırken hata: {e}")
        return False

def main():
    """Ana fonksiyon - tüm scriptleri sırayla çalıştırır"""
    print("\n" + "="*60)
    print("🔥 AKARYAKIT FİYATLARI TOPLAMA İŞLEMİ BAŞLIYOR")
    print("="*60)
    print(f"📅 Başlangıç: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
    print(f"📋 Toplam {len(SCRIPTS)} script çalıştırılacak\n")
    
    basarili = []
    basarisiz = []
    baslangic = datetime.now()
    
    # Her scripti sırayla çalıştır
    for i, script in enumerate(SCRIPTS, 1):
        print(f"\n[{i}/{len(SCRIPTS)}] İşlem yapılıyor...")
        
        if run_script(script):
            basarili.append(script)
        else:
            basarisiz.append(script)
            
        # Son script değilse kısa bir bekleme
        if i < len(SCRIPTS):
            print("\n⏳ Sonraki scripte geçiliyor...")
    
    # Özet rapor
    bitis = datetime.now()
    sure = (bitis - baslangic).total_seconds()
    
    print("\n" + "="*60)
    print("📊 İŞLEM ÖZETI")
    print("="*60)
    print(f"⏱️  Toplam süre: {sure:.1f} saniye ({sure/60:.1f} dakika)")
    print(f"✅ Başarılı: {len(basarili)}/{len(SCRIPTS)}")
    print(f"❌ Başarısız: {len(basarisiz)}/{len(SCRIPTS)}")
    
    if basarili:
        print(f"\n✅ Başarılı scriptler:")
        for script in basarili:
            print(f"   ✓ {script}")
    
    if basarisiz:
        print(f"\n❌ Başarısız scriptler:")
        for script in basarisiz:
            print(f"   ✗ {script}")
    
    print("\n" + "="*60)
    print(f"🏁 İŞLEM TAMAMLANDI - {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
    print("="*60 + "\n")
    
    # Eğer bazı scriptler başarısız olduysa hata kodu döndür
    return 0 if len(basarisiz) == 0 else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
