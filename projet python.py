from tkinter import *
from tkinter.messagebox import *
import sqlite3

#wafin a siham
db = sqlite3.connect("gestion_hopital.db")
db.row_factory = sqlite3.Row

db.execute("CREATE TABLE IF NOT EXISTS patients(id_patient INTEGER PRIMARY KEY AUTOINCREMENT,CIN TEXT UNIQUE,nom TEXT,prenom TEXT,date_naissance TEXT,telephone TEXT)")

db.execute("CREATE TABLE IF NOT EXISTS medecins(id_medecin INTEGER PRIMARY KEY AUTOINCREMENT,nom TEXT,prenom TEXT,specialite TEXT,telephone TEXT)")

db.execute("CREATE TABLE IF NOT EXISTS rendezvous(id_rdv INTEGER PRIMARY KEY AUTOINCREMENT,id_patient INTEGER,id_medecin INTEGER,date_rdv TEXT,heure_rdv TEXT,motif TEXT,FOREIGN KEY(id_patient) REFERENCES patients(id_patient),FOREIGN KEY(id_medecin) REFERENCES medecins(id_medecin))")

db.commit()

# -------------------- Patients --------------------
def afficher_patients():
    list_patients.delete(0, END)


    list_patients.insert(END, f"{'ID':<5} | {'Nom':<20}| {'Prénom':<20} | {'CIN':<10} | {'Date Naissance':<12} | {'Téléphone':<12} ")
    list_patients.insert(END, "-"*95)
    for row in db.execute("SELECT * FROM patients"):
        list_patients.insert(END, f"{row['id_patient']:<5} | {row['nom']:<19} | {row['prenom']:<20} | {row['CIN']:<10} | {row['date_naissance']:<14} | {row['telephone']:<12} ")


def ajouter_patient():
    nom = ent_nom_p.get()
    prenom = ent_prenom_p.get()
    CIN=ent_CIN_p.get()
    date_naiss = f"{jour_var.get()}-{mois_var.get()}-{annee_var.get()}"
    tel = ent_tel_p.get()
    if not nom or not prenom or not date_naiss or not tel or not CIN :
        showerror("Erreur","Tous les champs sont obligatoires !")
        return
    cursor = db.execute("SELECT * FROM patients WHERE CIN = ?", (CIN,))
    if cursor.fetchone():
        showerror("Erreur", "CIN EXISTE DEJA !")
        return
    db.execute("INSERT INTO patients(nom, prenom,CIN,date_naissance, telephone) VALUES(?,?,?,?,?)",(nom, prenom,CIN,date_naiss, tel))
    db.commit()
    afficher_patients()

def modifier_patient():
    selection = list_patients.curselection()
    if not selection:
        showerror("Erreur", "Sélectionnez un patient")
        return

    # Récupérer l'ID du patient sélectionné directement depuis le texte affiché
    idp = list_patients.get(selection[0]).split("|")[0]

    # Récupérer les infos actuelles du patient
    patient = None
    curseur = db.execute("SELECT * FROM patients WHERE id_patient=?", (idp,))
    for row in curseur:
        patient = row
        break  # prendre seulement la première ligne

    # Création du popup pour modification
    popup = Toplevel()
    popup.title("Modifier Patient")
    popup.geometry("300x250")

    Label(popup, text="Nom").grid(row=0, column=0,padx=5,pady=5)
    ent_nom = Entry(popup)
    ent_nom.insert(0, patient['nom'])
    ent_nom.grid(row=0, column=1,padx=5,pady=5)

    Label(popup, text="Prénom").grid(row=1, column=0,padx=5,pady=5)
    ent_prenom = Entry(popup)
    ent_prenom.insert(0, patient['prenom'])
    ent_prenom.grid(row=1, column=1,padx=5,pady=5)

    Label(popup, text="CIN").grid(row=2, column=0,padx=5,pady=5)
    ent_CIN = Entry(popup)
    ent_CIN.insert(0, patient['CIN'])
    ent_CIN.grid(row=2, column=1)

    Label(popup, text="Date Naissance").grid(row=3, column=0,padx=5,pady=5)
    frame_date = Frame(popup)
    frame_date.grid(row=3, column=1, padx=5, pady=5)

    j, m, a = patient['date_naissance'].split('-')
    jour_var = StringVar(value=j)
    mois_var = StringVar(value=m)
    annee_var = StringVar(value=a)

    jours = [str(i) for i in range(1, 32)]
    mois = [str(i) for i in range(1, 13)]
    annees = [str(i) for i in range(2026, 1925, -1)]

    OptionMenu(frame_date, jour_var, *jours).pack(side=LEFT)
    OptionMenu(frame_date, mois_var, *mois).pack(side=LEFT)
    OptionMenu(frame_date, annee_var, *annees).pack(side=LEFT)

    Label(popup, text="Téléphone").grid(row=4, column=0,padx=5,pady=5)
    ent_tel = Entry(popup)
    ent_tel.insert(0, patient['telephone'])
    ent_tel.grid(row=4, column=1,padx=5,pady=5)

    # Fonction interne pour valider les modifications
    def valider_modif():
        nom = ent_nom.get()
        prenom = ent_prenom.get()
        cin = ent_CIN.get()
        date_naiss = f"{jour_var.get()}-{mois_var.get()}-{annee_var.get()}"
        tel = ent_tel.get()
        if not nom or not prenom or not date_naiss or not tel or not cin:
            showerror("Erreur", "Tous les champs sont obligatoires")
            return
        cursor = db.execute("SELECT * FROM patients WHERE CIN = ? AND id_patient <> ?", (cin,idp))
        if cursor.fetchone():
            showerror("Erreur", "CIN EXISTE DEJA !")
            return
        db.execute("UPDATE patients SET nom=?, prenom=?,CIN =? ,date_naissance=?, telephone=? WHERE id_patient=?",(nom, prenom,cin ,date_naiss, tel, idp))
        db.commit()
        afficher_patients()
        popup.destroy()  # fermer le popup

    Button(popup, text="Valider", command=valider_modif).grid(row=5, column=0, columnspan=2,pady=10)



def supprimer_patient():
    selection = list_patients.curselection()
    if not selection:
        showerror("Erreur","Sélectionnez un patient")
        return
    idp = list_patients.get(selection[0]).split("|")[0]
    confirme = askyesno("SUPPRIMER UN PATIENT", "Êtes-vous sûr ?")
    if confirme: 
        db.execute("DELETE FROM patients WHERE id_patient=?", (idp,))
        db.commit()
        afficher_patients()

def rechercher_patient():
    nom = ent_rech_nom.get().strip()
    prenom = ent_rech_prenom.get().strip()
    cin=ent_rech_cin.get().strip()
    
    if not nom and not prenom and not cin:
        showerror("Erreur", "Saisir au moins une information")
        return
    
    # Création de la fenêtre secondaire pour afficher les résultats
    fen_rech = Toplevel(fen)
    fen_rech.title("Résultats Recherche Patient")
    fen_rech.geometry("800x400")

    list_result = Listbox(fen_rech, font=("Courier New", 10), width=70, height=20)
    list_result.pack(padx=10, pady=10, fill=BOTH, expand=True)

    # En-tête
    list_result.insert(END, f"{'ID':<5} | {'Nom':<20} | {'Prénom':<20} |{'CIN':<10}| {'Date Naissance':<12} | {'Téléphone':<12}")
    list_result.insert(END, "-"*100)

    # Remplissage de la liste avec les résultats
    for row in db.execute("SELECT * FROM patients WHERE nom LIKE ? AND prenom LIKE ? AND CIN LIKE ?", (f"%{nom}%", f"%{prenom}%", f"%{cin}%")):
        list_result.insert(END, f"{row['id_patient']:<5} | {row['nom']:<20} | {row['prenom']:<20} | {row['CIN']:<8} | {row['date_naissance']:<14} | {row['telephone']:<12}")
        

# -------------------- Médecins --------------------
def afficher_medecins():
    list_medecins.delete(0, END)
    list_medecins.insert(END, f"{'ID':<5} | {'Nom':<20} |{'Prénom':<20} | {'Spécialité':<25} | {'Téléphone':<15}")
    list_medecins.insert(END, "-"*95)
    for row in db.execute("SELECT * FROM medecins"):
        list_medecins.insert(END, f"{row['id_medecin']:<5} | {row['nom']:<20} | {row['prenom']:<19} | {row['specialite']:<25} | {row['telephone']:<15}")

def ajouter_medecin():
    nom = ent_nom_m.get()
    prenom = ent_prenom_m.get()
    spec = ent_spec_m.get()
    tel = ent_tel_m.get()
    if not nom or not spec or not tel or not prenom:
        showerror("Erreur","Tous les champs sont obligatoires")
        return
    db.execute("INSERT INTO medecins(nom,prenom, specialite, telephone) VALUES(?,?,?,?)",(nom, prenom,spec, tel))
    db.commit()
    afficher_medecins()

def modifier_medecin():
    selection = list_medecins.curselection()
    if not selection:
        showerror("Erreur", "Sélectionnez un médecin")
        return

    # Récupérer l'ID du médecin sélectionné
    idm = list_medecins.get(selection[0]).split("|")[0]

    # Récupérer les infos actuelles du médecin
    medecin = None
    curseur = db.execute("SELECT * FROM medecins WHERE id_medecin=?", (idm,))
    for row in curseur:
        medecin = row
        break  # on prend seulement la première ligne


    # Création du popup pour modification
    popup = Toplevel()
    popup.geometry("250x200")
    popup.title("Modifier Médecin")

    Label(popup, text="Nom").grid(row=0, column=0,padx=10,pady=10)
    ent_nom = Entry(popup)
    ent_nom.insert(0, medecin['nom'])
    ent_nom.grid(row=0, column=1,padx=10,pady=10)

    Label(popup, text="Prénom").grid(row=1, column=0,padx=10,pady=10)
    ent_prenom = Entry(popup)
    ent_prenom.insert(0, medecin['prenom'])
    ent_prenom.grid(row=1, column=1,padx=10,pady=10)

    Label(popup, text="Spécialité").grid(row=2, column=0,padx=10,pady=10)
    # Variable pour OptionMenu
    ent_spec = StringVar()
    ent_spec.set(medecin['specialite'])  # valeur actuelle
    option_spec = OptionMenu(popup, ent_spec, *specialite)
    option_spec.grid(row=2, column=1,padx=10,pady=10)
    

    Label(popup, text="Téléphone").grid(row=3, column=0,padx=10,pady=10)
    ent_tel = Entry(popup)
    ent_tel.insert(0, medecin['telephone'])
    ent_tel.grid(row=3, column=1,padx=10,pady=10)

    # Fonction interne pour valider les modifications
    def valider_modif():
        nom = ent_nom.get()
        prenom=ent_prenom.get()
        spec = ent_spec.get()
        tel = ent_tel.get()
        if not nom or not spec or not tel or not prenom:
            showerror("Erreur", "Tous les champs sont obligatoires")
            return
        db.execute("UPDATE medecins SET nom=?, prenom=?,specialite=?, telephone=? WHERE id_medecin=?",(nom,prenom, spec, tel, idm))
        db.commit()
        afficher_medecins()
        popup.destroy()  # fermer le popup

    Button(popup, text="Valider", command=valider_modif).grid(row=4, column=0, columnspan=2,pady=10)


def supprimer_medecin():
    selection = list_medecins.curselection()
    if not selection:
        showerror("Erreur","Sélectionnez un médecin")
        return
    idm = list_medecins.get(selection[0]).split("|")[0]
    confirme = askyesno("SUPPRIMER UN MEDECIN", "Êtes-vous sûr ?")
    if confirme: 
        db.execute("DELETE FROM medecins WHERE id_medecin=?", (idm,))
        db.commit()
        afficher_medecins()
    

def rechercher_medecin():
    nom = ent_rech_nom_m.get().strip()
    prenom=ent_rech_prenom_m.get().strip()
    spec = ent_rech_spec.get().strip()

    if not nom and not spec and not prenom:
        showerror("Erreur", "Saisir au moins un nom ou une spécialité")
        return

    fen_rech = Toplevel(fen)
    fen_rech.title("Résultats Recherche Médecin")
    fen_rech.geometry("800x400")

    list_result = Listbox(fen_rech, font=("Courier New", 10), width=70, height=20)
    list_result.pack(padx=10, pady=10, fill=BOTH, expand=True)

    list_result.insert(END, f"{'ID':<5} | {'Nom':<20} | {'Prénom':<20} |{'Spécialité':<25} | {'Téléphone':<15}")
    list_result.insert(END, "-"*96)

    for row in db.execute("SELECT * FROM medecins WHERE nom LIKE ? AND prenom LIKE ? AND specialite LIKE ?", (f"%{nom}%",f"%{prenom}%", f"%{spec}%")):
        list_result.insert(END, f"{row['id_medecin']:<5} | {row['nom']:<20} | {row['prenom']:<20} | {row['specialite']:<25} | {row['telephone']:<15}")


# -------------------- Rendez-vous --------------------

def ajouter_rdv():
    pid = ent_pid.get()
    mid = ent_mid.get()
    date_r = f"{jour_rdv.get()}-{mois_rdv.get()}-{annee_rdv.get()}"
    heure = f"{spin_heure.get()}:{spin_minute.get()}"
    motif = ent_motif.get()
    if not pid or not mid or not date_r or not heure or not motif:
        showerror("Erreur","Tous les champs sont obligatoires")
        return
    db.execute("INSERT INTO rendezvous(id_patient,id_medecin,date_rdv,heure_rdv,motif) VALUES(?,?,?,?,?)",(pid, mid, date_r, heure, motif))
    db.commit()
    afficher_rdv()

# -------------------- Afficher tous les rendez-vous --------------------
def afficher_rdv():
    list_rdv.delete(0, END)
    list_rdv.insert(END, f"{'ID':<5} | {'Patient':<20} | {'Médecin':<20} | {'Date':<12} | {'Heure':<5} | {'Motif':<20}")
    list_rdv.insert(END, "-"*90)
    for r in db.execute("SELECT * FROM rendezvous"):
        # Nom patient
        patient_nom = ""
        for p in db.execute("SELECT nom, prenom FROM patients WHERE id_patient=?", (r['id_patient'],)):
            patient_nom = p['nom'] + " " + p['prenom']
            break
        # Nom médecin
        medecin_nom = ""
        for m in db.execute("SELECT nom ,prenom FROM medecins WHERE id_medecin=?", (r['id_medecin'],)):
            medecin_nom = m['nom']+ " " + m['prenom']
            break
        list_rdv.insert(END, f"{r['id_rdv']:<5} | {patient_nom:<20} | {medecin_nom:<20} | {r['date_rdv']:<12} | {r['heure_rdv']:<5} | {r['motif']:<20}")
# -------------------- Recherche rendez-vous --------------------
def rechercher_rdv():
    pid = ent_rech_pid.get()
    mid = ent_rech_mid.get()
    datev = ent_rech_date.get().strip()

    fen_rech = Toplevel(fen)
    fen_rech.title("Résultats Recherche Rendez-vous")
    fen_rech.geometry("700x400")

    list_result = Listbox(fen_rech, font=("Courier New", 10), width=90, height=20)
    list_result.pack(padx=10, pady=10, fill=BOTH, expand=True)

    list_result.insert(END, f"{'ID':<4} | {'Patient':<20} | {'Médecin':<15} | {'Date':<10} | {'Heure':<5} | {'Motif':<20}")
    list_result.insert(END, "-"*90)

    query = "SELECT * FROM rendezvous WHERE 1=1"
    params = []
    if pid: query += " AND id_patient=?"; params.append(pid)
    if mid: query += " AND id_medecin=?"; params.append(mid)
    if datev: query += " AND date_rdv=?"; params.append(datev)

    for r in db.execute(query, tuple(params)):
        patient_nom = db.execute("SELECT nom, prenom FROM patients WHERE id_patient=?", (r['id_patient'],)).fetchone()
        medecin_nom = db.execute("SELECT nom FROM medecins WHERE id_medecin=?", (r['id_medecin'],)).fetchone()
        patient_nom_str = patient_nom['nom'] + " " + patient_nom['prenom'] if patient_nom else ""
        medecin_nom_str = medecin_nom['nom'] if medecin_nom else ""
        list_result.insert(END, f"{r['id_rdv']:<4} | {patient_nom_str:<20} | {medecin_nom_str:<15} | {r['date_rdv']:<10} | {r['heure_rdv']:<5} | {r['motif']:<20}")

# -------------------- Modifier rendez-vous --------------------
def modifier_rdv():
    selection = list_rdv.curselection()
    if not selection:
        showerror("Erreur", "Sélectionnez un rendez-vous")
        return

    # Récupérer l'ID du rendez-vous sélectionné
    idr = list_rdv.get(selection[0]).split("|")[0].strip()

    # Récupérer les infos actuelles du rendez-vous
    rdv = db.execute("SELECT * FROM rendezvous WHERE id_rdv=?", (idr,)).fetchone()
    if not rdv:
        showerror("Erreur", "Rendez-vous introuvable")
        return

    # Création du popup pour modification
    popup = Toplevel()
    popup.title("Modifier Rendez-vous")
    popup.geometry("300x250")

    Label(popup, text="ID Patient").grid(row=0, column=0,padx=5,pady=5)
    ent_pid_r = Entry(popup)
    ent_pid_r.insert(0, rdv['id_patient'])
    ent_pid_r.grid(row=0, column=1,padx=5,pady=5)

    Label(popup, text="ID Médecin").grid(row=1, column=0,padx=5,pady=5)
    ent_mid_r = Entry(popup)
    ent_mid_r.insert(0, rdv['id_medecin'])
    ent_mid_r.grid(row=1, column=1,padx=5,pady=5)

    # --- Date (listboxs) ---
    Label(popup, text="Date").grid(row=2, column=0, padx=5, pady=5)
    frame_date_rdv = Frame(popup)
    frame_date_rdv.grid(row=2, column=1, padx=5, pady=5)

    j, m, a = rdv['date_rdv'].split('-')
    jour_rdv = StringVar(value=j)
    mois_rdv = StringVar(value=m)
    annee_rdv = StringVar(value=a)

    jours = [str(i) for i in range(1, 32)]
    mois = [str(i) for i in range(1, 13)]
    annees = [str(i) for i in range(2026, 2030)]

    OptionMenu(frame_date_rdv, jour_rdv, *jours).pack(side=LEFT)
    OptionMenu(frame_date_rdv, mois_rdv, *mois).pack(side=LEFT)
    OptionMenu(frame_date_rdv, annee_rdv, *annees).pack(side=LEFT)

    # --- Heure (spinboxs) ---
    Label(popup, text="Heure").grid(row=3, column=0, padx=5, pady=5)
    frame_heure = Frame(popup)
    frame_heure.grid(row=3, column=1, padx=5, pady=5)

    h, mn = rdv['heure_rdv'].split(':')
    spin_heure = Spinbox(frame_heure, from_=8, to=18, width=3, format="%02.0f")
    spin_heure.delete(0, END)
    spin_heure.insert(0, h)
    spin_heure.pack(side=LEFT)

    spin_minute = Spinbox(frame_heure, from_=0, to=59, width=3, format="%02.0f")
    spin_minute.delete(0, END)
    spin_minute.insert(0, mn)
    spin_minute.pack(side=LEFT)


    Label(popup, text="Motif").grid(row=4, column=0,padx=5,pady=5)
    ent_motif_rv = Entry(popup)
    ent_motif_rv.insert(0, rdv['motif'])
    ent_motif_rv.grid(row=4, column=1,padx=5,pady=5)

    def valider_modif_rdv():
        pid = ent_pid_r.get()
        mid = ent_mid_r.get()
        date_r = f"{jour_rdv.get()}-{mois_rdv.get()}-{annee_rdv.get()}"
        heure = f"{spin_heure.get()}:{spin_minute.get()}"
        motif = ent_motif_rv.get()
        if not pid or not mid or not date_r or not heure or not motif:
            showerror("Erreur", "Tous les champs sont obligatoires")
            return
        db.execute(
            "UPDATE rendezvous SET id_patient=?, id_medecin=?, date_rdv=?, heure_rdv=?, motif=? WHERE id_rdv=?",
            (pid, mid, date_r, heure, motif, idr)
        )
        db.commit()
        afficher_rdv()
        popup.destroy()

    Button(popup, text="Valider", command=valider_modif_rdv).grid(row=5, column=0, columnspan=2, pady=5)


# -------------------- Supprimer rendez-vous --------------------
def supprimer_rdv():
    selection = list_rdv.curselection()
    if not selection:
        showerror("Erreur","Sélectionnez un rendez-vous")
        return
    idr = list_rdv.get(selection[0]).split("|")[0].strip()
    confirme = askyesno("SUPPRIMER UN RENDEZVOUS", "Êtes-vous sûr ?")
    if confirme: 
        db.execute("DELETE FROM rendezvous WHERE id_rdv=?", (idr,))
        db.commit()
        afficher_rdv()
    



# -------------------- Interface améliorée --------------------
fen = Tk()
fen.title("Gestion Hôpital")
fen.geometry("850x600")  # un peu plus large pour les tableaux


# -- Frames pour les onglets --
frame_patients = Frame(fen)
frame_medecins = Frame(fen)
frame_rdv = Frame(fen)

def afficher_onglet(frame):
    frame_patients.pack_forget()
    frame_medecins.pack_forget()
    frame_rdv.pack_forget()
    frame.pack(fill=BOTH, expand=YES, padx=10, pady=10)

# -- Onglets en haut --
frame_onglets = Frame(fen)
frame_onglets.pack(side=TOP, fill=X, pady=5)
btn_patients = Button(frame_onglets, text="Patients", command=lambda: afficher_onglet(frame_patients))
btn_patients.pack(side=LEFT, fill=X, expand=True)
btn_medecins = Button(frame_onglets, text="Médecins", command=lambda: afficher_onglet(frame_medecins))
btn_medecins.pack(side=LEFT, fill=X, expand=True)
btn_rdv = Button(frame_onglets, text="Rendez-vous", command=lambda: afficher_onglet(frame_rdv))
btn_rdv.pack(side=LEFT, fill=X, expand=True)

# -------------------- Frame Patients --------------------
Label(frame_patients, text="Nom du patient").grid(row=0, column=0, sticky=W, padx=5, pady=2)
ent_nom_p = Entry(frame_patients); ent_nom_p.grid(row=0, column=1, sticky=W, padx=5, pady=2)
Label(frame_patients, text="Prénom du patient").grid(row=1, column=0, sticky=W, padx=5, pady=2)
ent_prenom_p = Entry(frame_patients); ent_prenom_p.grid(row=1, column=1, sticky=W, padx=5, pady=2)
Label(frame_patients, text="CIN du patient").grid(row=2, column=0, sticky=W, padx=5, pady=2)
ent_CIN_p=Entry(frame_patients); ent_CIN_p.grid(row=2, column=1, sticky=W, padx=5, pady=2)
Label(frame_patients, text="Date Naissance du patient").grid(row=3, column=0, sticky=W, padx=5, pady=2)

# Sous-frame pour contenir jour, mois, année sur la même ligne
frame_date = Frame(frame_patients)
frame_date.grid(row=3, column=1, sticky=W, padx=5, pady=2)

# Variables
jour_var = StringVar(value="1")
mois_var = StringVar(value="1")
annee_var = StringVar(value="2000")

# Listes pour les menus
jours = [str(i) for i in range(1, 32)]
mois = [str(i) for i in range(1, 13)]
annees = [str(i) for i in range(2026, 1925,-1)]

# Menus déroulants côte à côte
OptionMenu(frame_date, jour_var, *jours).pack(side=LEFT)
OptionMenu(frame_date, mois_var, *mois).pack(side=LEFT)
OptionMenu(frame_date, annee_var, *annees).pack(side=LEFT)

Label(frame_patients, text="Téléphone du patient").grid(row=4, column=0, sticky=W, padx=5, pady=2)
ent_tel_p = Entry(frame_patients); ent_tel_p.grid(row=4, column=1, sticky=W, padx=5, pady=2)

Button(frame_patients, text="Ajouter le patient", command=ajouter_patient).grid(row=0, column=2,rowspan=4, pady=5)
Button(frame_patients, text="Modifier le patient", command=modifier_patient).grid(row=12, column=0,padx=30 ,pady=5,sticky=W)
Button(frame_patients, text="Supprimer le patient", command=supprimer_patient).grid(row=12, column=1,padx=30 ,pady=5,sticky=W)

Label(frame_patients, text="--- Recherche ---").grid(row=6, column=0, columnspan=2, pady=5,sticky=W)
Label(frame_patients, text="Nom").grid(row=7, column=0, sticky=W, padx=5)
ent_rech_nom = Entry(frame_patients); ent_rech_nom.grid(row=7, column=1, sticky=W, padx=5)
Label(frame_patients, text="Prénom").grid(row=8, column=0, sticky=W, padx=5)
ent_rech_prenom = Entry(frame_patients); ent_rech_prenom.grid(row=8, column=1, sticky=W, padx=5)
Label(frame_patients, text="CIN").grid(row=9, column=0, sticky=W, padx=5)
ent_rech_cin = Entry(frame_patients); ent_rech_cin.grid(row=9, column=1, sticky=W, padx=5)
Button(frame_patients, text="Rechercher", command=rechercher_patient).grid(row=7, column=2, rowspan=3, pady=10)

# Listbox Patients
list_patients = Listbox(frame_patients, width=95, height=15,font=("Courier New", 10))
list_patients.grid(row=11, column=0, columnspan=3, sticky="nsew", padx=5, pady=10)

afficher_patients()

# -------------------- Frame Médecins --------------------
Label(frame_medecins, text="Nom du medecin").grid(row=0, column=0, sticky=W, padx=5, pady=2)
ent_nom_m = Entry(frame_medecins); ent_nom_m.grid(row=0, column=1, sticky=W, padx=5, pady=2)
Label(frame_medecins, text="Prénom du medecin").grid(row=1, column=0, sticky=W, padx=5, pady=2)
ent_prenom_m = Entry(frame_medecins); ent_prenom_m.grid(row=1, column=1, sticky=W, padx=5, pady=2)
Label(frame_medecins, text="Spécialité du medecin").grid(row=2, column=0, sticky=W, padx=5, pady=2)
frame_spec = Frame(frame_medecins)
frame_spec.grid(row=2, column=1, sticky=W, padx=5, pady=2)
ent_spec_m= StringVar()
specialite = ["Médecin généraliste", "Dentiste", "Pédiatre", "Gynécologue/Obstétricien", "Cardiologue", "Dermatologue", "Ophtalmologiste", "Orthopédiste", "Psychiatre", "ORL (Oto-rhino-laryngologiste)"]
OptionMenu(frame_spec, ent_spec_m , *specialite).pack(side=LEFT,expand=TRUE)

Label(frame_medecins, text="Téléphone du medecin").grid(row=3, column=0, sticky=W, padx=5, pady=2)
ent_tel_m = Entry(frame_medecins); ent_tel_m.grid(row=3, column=1, sticky=W, padx=5, pady=2)

Button(frame_medecins, text="Ajouter le medecin", command=ajouter_medecin).grid(row=0,column=2,rowspan=3, pady=5)
Button(frame_medecins, text="Modifier le medecin", command=modifier_medecin).grid(row=11,column=0, pady=2,sticky=W,padx=30)
Button(frame_medecins, text="Supprimer le medecin", command=supprimer_medecin).grid(row=11,column=1, pady=2,sticky=W,padx=30)

Label(frame_medecins, text="--- Recherche ---").grid(row=4,column=0,columnspan=2, pady=5,sticky=W)
Label(frame_medecins, text="Nom du medecin").grid(row=5,column=0, sticky=W, padx=5, pady=5)
ent_rech_nom_m = Entry(frame_medecins); ent_rech_nom_m.grid(row=5,column=1, sticky=W, padx=5, pady=5)
Label(frame_medecins, text="Prénom du medecin").grid(row=6,column=0, sticky=W, padx=5, pady=5)
ent_rech_prenom_m = Entry(frame_medecins); ent_rech_prenom_m.grid(row=6,column=1, sticky=W, padx=5, pady=5)
Label(frame_medecins, text="Spécialité du medecin").grid(row=7,column=0, sticky=W, padx=5, pady=5)
frame_rech_spec = Frame(frame_medecins)
frame_rech_spec.grid(row=7, column=1, sticky=W, padx=5, pady=2)
ent_rech_spec= StringVar()
OptionMenu(frame_rech_spec, ent_rech_spec , *specialite).pack(side=LEFT,expand=TRUE)


Button(frame_medecins, text="Rechercher", command=rechercher_medecin).grid(row=6,column=2, pady=10,rowspan=3)

# Listbox Médecins
list_medecins = Listbox(frame_medecins, font=("Courier New", 10),width=95, height=15)
list_medecins.grid(row=10, column=0, columnspan=3, sticky="nsew", padx=5, pady=10)

afficher_medecins()

# -------------------- Frame Rendez-vous --------------------
Label(frame_rdv, text="ID Patient").grid(row=0, column=0, sticky=W, padx=5, pady=2)
ent_pid = Entry(frame_rdv); ent_pid.grid(row=0, column=1, sticky=W, padx=5, pady=2)
Label(frame_rdv, text="ID Médecin").grid(row=1, column=0, sticky=W, padx=5, pady=2)
ent_mid = Entry(frame_rdv); ent_mid.grid(row=1, column=1, sticky=W, padx=5, pady=2)
Label(frame_rdv, text="Date").grid(row=2, column=0, sticky=W, padx=5, pady=2)
# Sous-frame pour contenir jour, mois, année sur la même ligne
frame_date_r = Frame(frame_rdv)
frame_date_r.grid(row=2, column=1, sticky=W, padx=5, pady=2)

# Variables
jour_rdv = StringVar()
mois_rdv = StringVar()
annee_rdv = StringVar()

# Listes pour les menus
jours_r = [str(i) for i in range(1, 32)]
mois_r = [str(i) for i in range(1, 13)]
annees_r = [str(i) for i in range(2025, 2030)]

# Menus déroulants côte à côte
OptionMenu(frame_date_r, jour_rdv, *jours_r).pack(side=LEFT)
OptionMenu(frame_date_r, mois_rdv, *mois_r).pack(side=LEFT)
OptionMenu(frame_date_r, annee_rdv, *annees_r).pack(side=LEFT)

Label(frame_rdv, text="Heure").grid(row=3, column=0, sticky=W, padx=5, pady=2)
frame_heure = Frame(frame_rdv)
frame_heure.grid(row=3, column=1, sticky=W, padx=5, pady=2)

# Spinbox pour les heures (00–23)
spin_heure = Spinbox(frame_heure, from_=8, to=18, width=3, format="%02.0f")
spin_heure.pack(side=LEFT)

Label(frame_heure, text=":").pack(side=LEFT)

# Spinbox pour les minutes (00–59)
spin_minute = Spinbox(frame_heure, from_=0, to=59, width=3, format="%02.0f")
spin_minute.pack(side=LEFT)

Label(frame_rdv, text="Motif").grid(row=4, column=0, sticky=W, padx=5, pady=2)
ent_motif = Entry(frame_rdv); ent_motif.grid(row=4, column=1, sticky=W, padx=5, pady=2)

Button(frame_rdv, text="Ajouter le rendez-vous", command=ajouter_rdv).grid(row=0,column=2,rowspan=5, pady=5)
Button(frame_rdv, text="Modifier le rendez-vous", command=modifier_rdv).grid(row=13,column=0, pady=5,padx=30)
Button(frame_rdv, text="Supprimer le rendez-vous", command=supprimer_rdv).grid(row=13,column=1, pady=5,padx=30)

# Recherche rendez-vous
Label(frame_rdv, text="--- Recherche ---").grid(row=7,column=0,columnspan=2, pady=5,sticky=W)
Label(frame_rdv, text="ID Patient").grid(row=8,column=0, sticky=W, padx=5)
ent_rech_pid = Entry(frame_rdv); ent_rech_pid.grid(row=8,column=1, sticky=W, padx=5)
Label(frame_rdv, text="ID Médecin").grid(row=9,column=0, sticky=W, padx=5)
ent_rech_mid = Entry(frame_rdv); ent_rech_mid.grid(row=9,column=1, sticky=W, padx=5)
Label(frame_rdv, text="Date").grid(row=10,column=0, sticky=W, padx=5)
ent_rech_date = Entry(frame_rdv); ent_rech_date.grid(row=10,column=1, sticky=W, padx=5)
Button(frame_rdv, text="Rechercher", command=rechercher_rdv).grid(row=8,column=2,rowspan=3, pady=10)

# Listbox Rendez-vous
list_rdv = Listbox(frame_rdv, width=90, height=13,font=("Courier New", 10))
list_rdv.grid(row=12, column=0, columnspan=3, sticky="nsew", padx=5, pady=10)
afficher_rdv()

# Onglet par défaut
afficher_onglet(frame_patients)
fen.mainloop()

