import tkinter as tk, threading, time
root = tk.Tk()
hits = []
def worker():
    time.sleep(1)
    try:
        root.after(0, lambda: (hits.append(1), root.destroy()))
    except Exception as e:
        print("AFTER-FROM-THREAD RAISED:", e); root.destroy()
threading.Thread(target=worker, daemon=True).start()
root.after(10000, root.destroy)
root.mainloop()
print("hits:", len(hits), "=> after-from-thread", "WORKS" if hits else "BROKEN")
