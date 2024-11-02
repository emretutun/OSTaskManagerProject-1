import psutil
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# Ana Ekran 
root = tk.Tk()
root.title("Sistem Performans Monitörü")
root.geometry("800x600")

# Ana çerçeve
frame = tk.Frame(root)
frame.pack(fill=tk.BOTH, expand=True)

# Kaydırma çubukları ve tuval oluşturma
canvas = tk.Canvas(frame)
scroll_y = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
scroll_x = tk.Scrollbar(frame, orient="horizontal", command=canvas.xview)
scroll_y.pack(side="right", fill="y")
scroll_x.pack(side="bottom", fill="x")
canvas.pack(side="left", fill="both", expand=True)

# Kaydırma çerçevesi
scrollable_frame = tk.Frame(canvas)
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

def on_frame_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

scrollable_frame.bind("<Configure>", on_frame_configure)

# Başlık etiketleri
header = tk.Label(scrollable_frame, text="PID", width=10, anchor="w")
header.grid(row=0, column=0, padx=5, pady=5)
header = tk.Label(scrollable_frame, text="Süreç Adı", width=20, anchor="w")
header.grid(row=0, column=1, padx=5, pady=5)
header = tk.Label(scrollable_frame, text="CPU Kullanımı (%)", width=15, anchor="w")
header.grid(row=0, column=2, padx=5, pady=5)
header = tk.Label(scrollable_frame, text="Bellek Kullanımı (%)", width=15, anchor="w")
header.grid(row=0, column=3, padx=5, pady=5)

# Daire grafik verileri
def update_pie_chart(cpu_usage, memory_usage):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 4))  # İki ayrı eksen oluşturma
    # CPU Kullanımı Daire Grafiği
    labels_cpu = ['Kullanılan', 'Kullanılmayan']  # Etiketleri kısalttım
    sizes_cpu = [cpu_usage, 100 - cpu_usage]
    colors_cpu = ['blue', 'lightgray']
    ax1.pie(sizes_cpu, labels=labels_cpu, colors=colors_cpu,
            autopct='%.2f%%', shadow=True, startangle=90)  # İki ondalık basamak
    ax1.axis('equal')  # Dairenin daire şeklinde görünmesi için
    ax1.set_title("CPU Kullanımı")

    # Bellek Kullanımı Daire Grafiği
    labels_memory = ['Kullanılan', 'Kullanılmayan']  # Etiketleri kısalttım
    sizes_memory = [memory_usage, 100 - memory_usage]
    colors_memory = ['red', 'lightgray']
    ax2.pie(sizes_memory, labels=labels_memory, colors=colors_memory,
            autopct='%.2f%%', shadow=True, startangle=90)  # İki ondalık basamak
    ax2.axis('equal')  # Dairenin daire şeklinde görünmesi için
    ax2.set_title("Bellek Kullanımı")

    return fig

# Global canvas_plot değişkenini tanımlama
canvas_plot = None

# İlk başta boş grafik oluştur
fig = update_pie_chart(0, 0)
canvas_plot = FigureCanvasTkAgg(fig, master=root)
canvas_plot.get_tk_widget().pack(side="top", padx=10, pady=10)

def update_process_list():
    global canvas_plot  # canvas_plot değişkenini global olarak kullan
    # Önceki süreç bilgilerini temizle
    for widget in scrollable_frame.winfo_children():
        if int(widget.grid_info()["row"]) > 0:
            widget.destroy()

    # CPU ve bellek kullanımını al
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_usage = psutil.virtual_memory().percent

    # Her süreci güncelle
    for idx, process in enumerate(psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']), start=1):
        try:
            tk.Label(scrollable_frame, text=process.info['pid'], width=10, anchor="w").grid(row=idx, column=0, padx=5)
            tk.Label(scrollable_frame, text=process.info['name'], width=20, anchor="w").grid(row=idx, column=1, padx=5)
            tk.Label(scrollable_frame, text=f"{process.info['cpu_percent']}%", width=15, anchor="w").grid(row=idx, column=2, padx=5)
            # Bellek kullanımını 2 ondalık basamakla göster
            tk.Label(scrollable_frame, text=f"{process.info['memory_percent']:.2f}%", width=15, anchor="w").grid(row=idx, column=3, padx=5)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    # Daire grafik güncelle
    fig = update_pie_chart(cpu_usage, memory_usage)
    
    # Önceki grafik widget'ı varsa kaldır
    if canvas_plot:
        canvas_plot.get_tk_widget().destroy()
    
    # Yeni grafik oluşturma
    canvas_plot = FigureCanvasTkAgg(fig, master=root)
    canvas_plot.get_tk_widget().pack(side="top", padx=10, pady=10)

    # x saniyede bir güncelle
    root.after(50000, update_process_list)

update_process_list()
root.mainloop()
