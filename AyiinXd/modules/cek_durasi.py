import os
from AyiinXd import ayiin_cmd  # pastikan import ini benar

@ayiin_cmd(pattern="cekdurasi")
async def cek_durasi(event):
    try:
        # Ambil durasi dari environment variable, dengan default 30hari
        durasi = os.environ.get("DURASI_UBOT", "30hari").lower()
        
        # Log durasi untuk memastikan value yang terbaca
        print(f"DURASI_UBOT: {durasi}")  # Debugging untuk melihat apakah nilai terbaca
        
        # Mengatur durasi berdasarkan value
        if "hari" in durasi:
            # Jika durasi dalam format 'Xhari', ambil angka sebelum 'hari'
            days = int(durasi.replace("hari", ""))
            await event.edit(f"Durasi Userbot: {days} hari")
        elif "lifetime" in durasi:
            # Jika durasi adalah lifetime, tampilkan 'Lifetime'
            await event.edit(f"Durasi Userbot: Lifetime (selama bot berjalan)")
        else:
            # Jika bukan dalam format yang dikenali, tampilkan durasi mentah
            await event.edit(f"Durasi Userbot: {durasi}")
    except Exception as e:
        # Jika terjadi error, tampilkan error message
        await event.edit(f"Terjadi error: {str(e)}")
        print(f"Error: {str(e)}")
