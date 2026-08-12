import sqlite3
import tkinter as tk
from tkinter import messagebox,ttk
from PIL import Image, ImageTk
import hashlib
import datetime

import plnenie

# REZERVOVANIE SPOJA:
# 1. Vo formulári "Vyhľadávanie spojov" vyplň Smer, Čas odchodu (HH:MM) a Dátum
# 2. Klikni na "Vyhľadať spoje" otvorí sa okno s nájdenými spojmi
# 3. Dvojklikom na vybraný spoj v tomto okne sa spoj rezervuje

class Program(tk.Tk):
    def __init__(self):
        super().__init__()
        self.db = sqlite3.connect("databaza.db")  
        self.cursor = self.db.cursor()
        self.vytvor_okno()
        self.login_frame()


    def main_frame(self,id ,meno, mode):
        self.prihlaseny_id = id
        self.meno = meno
        if mode == 1:
            self.mode = "Admin"
        else:
            self.mode = "User"

        sirka = self.width * 0.8
        vyska = self.height * 0.8

        hlavny_frame = tk.Frame(self.canvas, width=sirka, height=vyska, bg="white")
        hlavny_frame.propagate(False)
        self.main_frame_widget = hlavny_frame
        self.canvas.create_window(self.width * 0.1, self.height * 0.1, window=hlavny_frame, anchor="nw")

        horna_lista = tk.Frame(hlavny_frame, bg="#dddddd", height=40)
        horna_lista.pack(fill="x", side="top")

        tk.Label(horna_lista, text=f"Používateľ: {self.meno}", bg="#dddddd", font=("Segoe UI", 12)).pack(side="left", padx=10)
        tk.Label(horna_lista, text=f"Mód: {self.mode}", bg="#dddddd", font=("Segoe UI", 12)).pack(side="right", padx=10)

        vyber_panel = tk.LabelFrame(hlavny_frame, text="Vyhľadávanie spojov", bg="white", fg="black",
                            font=("Segoe UI", 12, "bold"), bd=2, relief="groove", padx=10, pady=10)
        vyber_panel.place(x=sirka*0.05, y=100, width=400)  

        
        tk.Label(vyber_panel, text="Smer:", bg="white", font=("Segoe UI", 12)).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        smer_entry = tk.Entry(vyber_panel, font=("Segoe UI", 12))
        smer_entry.grid(row=0, column=1, padx=5, pady=5)

        
        tk.Label(vyber_panel, text="Čas odchodu (HH:MM):", bg="white", font=("Segoe UI", 12)).grid(row=1, column=0, padx=5, pady=5, sticky="e")
        cas_entry = tk.Entry(vyber_panel, font=("Segoe UI", 12))
        cas_entry.grid(row=1, column=1, padx=5, pady=5)

        
        tk.Label(vyber_panel, text="Dátum: RRRR / MM / DD", bg="white", font=("Segoe UI", 12)).grid(row=2, column=0, padx=5, pady=5, sticky="e")
        rok_entry = tk.Entry(vyber_panel, width=5, font=("Segoe UI", 12))
        rok_entry.grid(row=2, column=1, sticky="w", padx=(0, 2))

        mesiac_entry = tk.Entry(vyber_panel, width=3, font=("Segoe UI", 12))
        mesiac_entry.grid(row=2, column=1, padx=(0, 2))

        den_entry = tk.Entry(vyber_panel, width=3, font=("Segoe UI", 12))
        den_entry.grid(row=2, column=1, padx=(90, 0))

        
        tk.Button(vyber_panel, text="Vyhľadať spoje", font=("Segoe UI", 12, "bold"),
                command=lambda: self.vyhladaj_spoje_do_okna(
                    smer_entry.get(),
                    cas_entry.get(),
                    rok_entry.get(),
                    mesiac_entry.get(),
                    den_entry.get()
                )).grid(row=3, column=0, columnspan=2, pady=10)



        pravy_panel = tk.Frame(hlavny_frame, width=sirka/2, height=vyska, bg="white")
        pravy_panel.place(x=(sirka/2)-5, y=40)

        style = ttk.Style()
        style.configure("Treeview", rowheight=50, font=("Segoe UI", 15))
        style.configure("Treeview.Heading", font=("Segoe UI", 15, "bold"))
        
        odchody_label = tk.Label(pravy_panel, text="Najbližších 5 odchodov", bg="white", font=("Segoe UI", 10, "bold"))
        odchody_label.pack(pady=(0, 5))

        odchody_tree = ttk.Treeview(pravy_panel, columns=("cislo", "datum", "cas", "smer"), show="headings", height=5)
        odchody_tree.heading("cislo", text="Linka", command=lambda: self.zorad_treeview(odchody_tree, "cislo"))
        odchody_tree.heading("datum", text="Dátum", command=lambda: self.zorad_treeview(odchody_tree, "datum"))
        odchody_tree.heading("cas", text="Čas", command=lambda: self.zorad_treeview(odchody_tree, "cas"))
        odchody_tree.heading("smer", text="Trasa", command=lambda: self.zorad_treeview(odchody_tree, "smer"))


        total_width = int(sirka / 2)

        
        linka_width = total_width // 8
        ostatne_width = (total_width - linka_width) // 3

        
        odchody_tree.column("cislo", width=linka_width, anchor="center")
        odchody_tree.column("datum", width=ostatne_width, anchor="center")
        odchody_tree.column("cas", width=ostatne_width, anchor="center")
        odchody_tree.column("smer", width=ostatne_width, anchor="center")

        odchody_tree.pack(pady=(0, 20), fill="both", expand=True)

        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

        
        self.cursor.execute("""
            SELECT linky.cislo_linky, odchody.datum, odchody.cas, linky.nazov
            FROM odchody
            JOIN linky ON odchody.id_linky = linky.id
            WHERE datetime(odchody.datum || ' ' || odchody.cas) >= datetime(?)
            GROUP BY linky.cislo_linky
            ORDER BY odchody.datum, odchody.cas
            LIMIT 5
        """, (now,))

        for row in self.cursor.fetchall():
            odchody_tree.insert("", "end", values=row)

        
        prichody_label = tk.Label(pravy_panel, text="Najbližších 5 príchodov", bg="white", font=("Segoe UI", 10, "bold"))
        prichody_label.pack(pady=(0, 5))

        prichody_tree = ttk.Treeview(pravy_panel, columns=("cislo", "datum", "cas", "smer"), show="headings", height=5)
        prichody_tree.heading("cislo", text="Linka")
        prichody_tree.heading("datum", text="Dátum")
        prichody_tree.heading("cas", text="Čas")
        prichody_tree.heading("smer", text="Smer")



        prichody_tree.column("cislo", width=linka_width, anchor="center")
        prichody_tree.column("datum", width=ostatne_width, anchor="center")
        prichody_tree.column("cas", width=ostatne_width, anchor="center")
        prichody_tree.column("smer", width=ostatne_width, anchor="center")

        prichody_tree.pack(fill="both", expand=True)

        self.cursor.execute("""
            SELECT linky.cislo_linky, prichody.datum, prichody.cas, linky.nazov
            FROM prichody
            JOIN linky ON prichody.id_linky = linky.id
            WHERE datetime(prichody.datum || ' ' || prichody.cas) >= datetime(?)
            GROUP BY linky.cislo_linky
            ORDER BY prichody.datum, prichody.cas
            LIMIT 5
        """, (now,))

        for row in self.cursor.fetchall():
            prichody_tree.insert("", "end", values=row)

        self.zobraz_rezervacie(sirka,vyska,hlavny_frame)

    def zobraz_rezervacie(self, sirka, vyska, hlavny_frame):

        rezervacie_frame = tk.Frame(hlavny_frame, bg="white")
        rezervacie_frame.place(x=10, y=int(vyska * 0.51), width=int(sirka * 0.48), height=int(vyska * 0.45))

        tk.Label(rezervacie_frame, text="Moje rezervácie", font=("Segoe UI", 14, "bold"), bg="white").pack(pady=(0, 10))

        tree = ttk.Treeview(rezervacie_frame, columns=("cislo", "datum", "cas", "nazov"), show="headings", height=5)
        tree.heading("cislo", text="Linka", command=lambda: self.zorad_treeview(tree, "cislo"))
        tree.heading("datum", text="Dátum", command=lambda: self.zorad_treeview(tree, "datum"))
        tree.heading("cas", text="Čas", command=lambda: self.zorad_treeview(tree, "cas"))
        tree.heading("nazov", text="Trasa", command=lambda: self.zorad_treeview(tree, "nazov"))

        for col in ("cislo", "datum", "cas", "nazov"):
            tree.column(col, anchor="center")

        tree.pack(fill="both", expand=True, padx=10, pady=5)

        self.rezervacie_tree = tree

        self.naplni_rezervacie()

    def naplni_rezervacie(self):
        # vymaže staré riadky
        for row in self.rezervacie_tree.get_children():
            self.rezervacie_tree.delete(row)

        self.cursor.execute("""
            SELECT linky.cislo_linky, odchody.datum, odchody.cas, linky.nazov
            FROM rezervacie
            JOIN odchody ON rezervacie.id_odchodu = odchody.id
            JOIN linky ON odchody.id_linky = linky.id
            WHERE rezervacie.id_pouzivatel = ?
            ORDER BY odchody.datum, odchody.cas
        """, (self.prihlaseny_id,))

        for row in self.cursor.fetchall():
            self.rezervacie_tree.insert("", "end", values=row)


    def vycisti_stare_spoje(self):
        teraz = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

        self.cursor.execute("""
            DELETE FROM rezervacie
            WHERE id_odchodu IN (
                SELECT id FROM odchody
                WHERE datetime(datum || ' ' || cas) < datetime(?)
            )
        """, (teraz,))
        self.cursor.execute("""
            DELETE FROM odchody
            WHERE datetime(datum || ' ' || cas) < datetime(?)
        """, (teraz,))

        self.cursor.execute("""
            DELETE FROM prichody
            WHERE datetime(datum || ' ' || cas) < datetime(?)
        """, (teraz,))

        self.db.commit()

        
    def zorad_treeview(self, tree, stlpec, reverzne=False):
        data = [(tree.set(k, stlpec), k) for k in tree.get_children('')]

        try:
            data.sort(reverse=reverzne, key=lambda t: int(t[0]) if t[0].isdigit() else t[0])
        except:
            data.sort(reverse=reverzne)

        for index, (val, k) in enumerate(data):
            tree.move(k, '', index)

       
        tree.heading(stlpec, command=lambda: self.zorad_treeview(tree, stlpec, not reverzne))

    def vyhladaj_spoje_do_okna(self, ciel, cas, rok, mesiac, den):
        
        for widget in self.canvas.winfo_children():
            if isinstance(widget, tk.Toplevel):
                widget.destroy()

        
        try:
            parsed_time = datetime.datetime.strptime(cas.strip(), "%H:%M")
            cas = parsed_time.strftime("%H:%M")  
        except ValueError:
            messagebox.showerror("Chybný čas", "Zadaj čas vo formáte HH:MM.")
            return

       
        if rok and mesiac and den:
            try:
                datum = f"{int(rok):04d}-{int(mesiac):02d}-{int(den):02d}"
                datetime.datetime.strptime(datum, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Chybný dátum", "Zadaj platný dátum vo formáte RRRR-MM-DD.")
                return
        else:
            datum = datetime.datetime.now().strftime("%Y-%m-%d")

        query_time = f"{datum} {cas}"

      
        okno = tk.Toplevel(self)
        okno.title("Dostupné spoje")
        okno.geometry("750x400")
        okno.configure(bg="white")
        self.otvorene_okno = okno

        vysledky_tree = ttk.Treeview(okno, columns=("cislo", "datum", "cas", "smer"), show="headings", height=5)
        for col, label in [("cislo", "Linka"), ("datum", "Dátum"), ("cas", "Čas"), ("smer", "Trasa")]:
            vysledky_tree.heading(col, text=label)
            vysledky_tree.column(col, width=180, anchor="center")

        vysledky_tree.pack(padx=20, pady=20, fill="both", expand=True)

        self.cursor.execute("""
            SELECT linky.cislo_linky, odchody.datum, odchody.cas, linky.nazov
            FROM odchody
            JOIN linky ON odchody.id_linky = linky.id
            WHERE linky.ciel = ? AND datetime(odchody.datum || ' ' || odchody.cas) >= datetime(?)
            ORDER BY odchody.datum, odchody.cas
            LIMIT 5
        """, (ciel, query_time))

        for row in self.cursor.fetchall():
            vysledky_tree.insert("", "end", values=row)

        
        vysledky_tree.bind("<Double-1>", lambda e: self.rezervuj_odchod(vysledky_tree, okno))

       
        tk.Button(okno, text="Zavrieť", font=("Segoe UI", 11), command=okno.destroy).pack(pady=5)

    def rezervuj_odchod(self, tree, okno=None):
        vybrane = tree.selection()
        if not vybrane:
            messagebox.showwarning("Výber", "Vyber spoj, ktorý chceš rezervovať.")
            return

        hodnoty = tree.item(vybrane[0])["values"]
        cislo_linky, datum, cas, nazov = hodnoty

        self.cursor.execute("""
            SELECT odchody.id, odchody.volne_miesta
            FROM odchody
            JOIN linky ON odchody.id_linky = linky.id
            WHERE linky.cislo_linky = ? AND odchody.datum = ? AND odchody.cas = ?
        """, (cislo_linky, datum, cas))
        vysledok = self.cursor.fetchone()

        if not vysledok:
            messagebox.showerror("Chyba", "Nepodarilo sa nájsť daný odchod.")
            return

        id_odchodu, volne_miesta = vysledok

        if volne_miesta <= 0:
            messagebox.showerror("Obsadené", "Na tento spoj už nie sú voľné miesta.")
            return

        self.cursor.execute("""
            SELECT COUNT(*) FROM rezervacie
            WHERE id_odchodu = ? AND id_pouzivatel = ?
        """, (id_odchodu, self.prihlaseny_id))

        if self.cursor.fetchone()[0] > 0:
            messagebox.showinfo("Info", "Už máš rezerváciu na tento spoj.")
            return

        self.cursor.execute("""
            INSERT INTO rezervacie (id_odchodu, id_pouzivatel, cas_rezervacie)
            VALUES (?, ?, datetime('now'))
        """, (id_odchodu, self.prihlaseny_id))

        self.cursor.execute("""
            UPDATE odchody SET volne_miesta = volne_miesta - 1 WHERE id = ?
        """, (id_odchodu,))

        self.db.commit()

        self.naplni_rezervacie()

        messagebox.showinfo("Rezervácia", "Rezervácia bola úspešne vytvorená.")
        if okno:
            okno.destroy()



    def zahashuj_heslo(self,heslo):
        return hashlib.sha256(heslo.encode()).hexdigest()

    def vytvor_okno(self):
        self.title("FMPH Bus")
        ikona = tk.PhotoImage(file="obrazky/Bus.png")
        self.iconphoto(True, ikona)
        

        
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

       
        self.width = int(screen_width * 0.8)
        self.height = int(screen_height * 0.8)
        self.x = (screen_width - self.width) // 2
        self.y = (screen_height - self.height) // 2

        
        self.geometry(f"{self.width}x{self.height}+{self.x}+{self.y}")


        bg_img = Image.open("obrazky/pozadie.webp")
        bg_img = bg_img.resize((self.width, self.height), Image.Resampling.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(bg_img)

        self.canvas = tk.Canvas(self, width=self.width, height=self.height)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")

    def login_frame(self):
        login_window_width = self.width*0.35
        login_window_height = self.height*0.5
        frame = tk.Frame(self.canvas, width=login_window_width, height=login_window_height, bg="white")
        frame.propagate(False)
        
        self.login_window = self.canvas.create_window(self.width*0.48, self.height*0.2, window=frame, anchor="nw")

     
        heading = tk.Label(frame, text='Sign in', fg='Red', bg='white', font=('Segoe UI', 25, 'bold'))
        heading.place(x=login_window_width*0.1, y=login_window_height*0.1)


        user = tk.Entry(frame, width=50, fg='black', border=0, bg='white', font=('Segoe UI', 15))
        user.place(x=login_window_width*0.1, y=login_window_height*0.3)
        user.insert(0, 'Username')
        tk.Frame(frame, width=login_window_width*0.8, height=2, bg='black').place(x=login_window_width*0.1, y=login_window_height*0.375)

        def on_user_click(event):
            if user.get() == 'Username':
                user.delete(0, tk.END)
                user.config(fg='black')

        def on_user_focusout(event):
            if user.get() == '':
                user.insert(0, 'Username')
                user.config(fg='grey')

        user.bind('<FocusIn>', on_user_click)
        user.bind('<FocusOut>', on_user_focusout)

        
        password = tk.Entry(frame, width=50, fg='black', border=0, bg='white', font=('Segoe UI', 15))
        password.place(x=login_window_width*0.1, y=login_window_height*0.5)
        password.insert(0, 'Password')
        tk.Frame(frame, width=login_window_width*0.8, height=2, bg='black').place(x=login_window_width*0.1, y=login_window_height*0.575)

        def on_password_click(event):
            if password.get() == 'Password':
                password.delete(0, tk.END)
                password.config(fg='black', show='*')

        def on_password_focusout(event):
            if password.get() == '':
                password.insert(0, 'Password')
                password.config(fg='grey', show='')

        password.bind('<FocusIn>', on_password_click)
        password.bind('<FocusOut>', on_password_focusout)


        def over_uzivatela():
            meno = user.get()
            heslo = password.get()


            self.cursor.execute("""SELECT * FROM uzivatelia where meno = ?""",(meno,))
            uzivatel = self.cursor.fetchone()

            
            if uzivatel and uzivatel[2]== self.zahashuj_heslo(heslo):
                messagebox.showinfo("Prihlásenie", "Úspešné prihlásenie!")
                self.vycisti_stare_spoje()

                self.canvas.delete(self.login_window)  
                self.main_frame(uzivatel[0],meno,uzivatel[3])

            else:
                messagebox.showerror("Chyba", "Zlé meno alebo heslo.")





        
        tk.Button(frame, command=over_uzivatela,text="Login", bg='red', fg='white', font=('Segoe UI', 15, 'bold'), width=15, height=1, border=0).place(x=login_window_width*0.3, y=login_window_height*0.7)




app = Program()
app.mainloop()