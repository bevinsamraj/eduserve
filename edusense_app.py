import os
import pickle
import pandas as pd
import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox
from transformers import pipeline
from textblob import TextBlob
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# --- Constants & Globals ---
DATA_FILE = "data/students.csv"
FEEDBACK_STORE = "data/manual_feedback.pkl"
RISK_MODEL_FILE = "models/risk_model.pkl"

# Load or init manual feedback storage
if os.path.exists(FEEDBACK_STORE):
    with open(FEEDBACK_STORE, "rb") as f:
        manual_feedback = pickle.load(f)
else:
    manual_feedback = {}

# --- Helper functions ---
def load_csv(path=DATA_FILE):
    df = pd.read_csv(path)
    df['Name'] = df['Student']
    return df

def save_csv(df, path):
    df.to_csv(path, index=False)

def save_pdf(feedback_dict, path):
    c = canvas.Canvas(path, pagesize=letter)
    w, h = letter
    c.setFont("Helvetica", 16)
    y = h - 40
    c.drawString(40, y, "EduSense: Personalized Feedback")
    y -= 40
    for name, fb in feedback_dict.items():
        if y < 80:
            c.showPage()
            y = h - 40
        c.setFont("Helvetica-Bold", 14)
        c.drawString(40, y, name)
        y -= 20
        c.setFont("Helvetica", 12)
        for line in fb.split("\n"):
            c.drawString(60, y, line)
            y -= 16
        y -= 12
    c.save()

def nlp_feedback(row):
    avg = (row['Math'] + row['Science'] + row['English']) / 3
    base = ("Excellent!" if avg >= 85 else "Good" if avg >= 70 else "Needs Improvement")
    tb_sent = TextBlob(row.get('Remarks', '')).sentiment
    return {
        "feedback": f"{base} Polarity:{tb_sent.polarity:.2f}, Subj:{tb_sent.subjectivity:.2f}",
        "polarity": tb_sent.polarity,
        "subjectivity": tb_sent.subjectivity
    }

def recommend_resources(row):
    areas = [s for s in ["Math", "Science", "English"] if row[s] < 70]
    links = {
        "Math": "https://www.khanacademy.org/math",
        "Science": "https://www.sciencebuddies.org/",
        "English": "https://www.grammarly.com/"
    }
    return [(a, links[a]) for a in areas]

def train_risk_model(df, thresh_avg, thresh_att):
    X = df[["Math", "Science", "English", "Attendance"]]
    y = (((X[["Math", "Science", "English"]].mean(axis=1) < thresh_avg) |
          (X["Attendance"] < thresh_att))).astype(int)
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X, y)
    os.makedirs(os.path.dirname(RISK_MODEL_FILE), exist_ok=True)
    pickle.dump(clf, open(RISK_MODEL_FILE, "wb"))
    return clf

def predict_risk(row, clf):
    return bool(clf.predict([[row['Math'], row['Science'], row['English'], row['Attendance']]])[0])

def get_topics(docs, n=3):
    vec = CountVectorizer(stop_words='english')
    X = vec.fit_transform(docs)
    lda = LatentDirichletAllocation(n_components=n, random_state=42)
    lda.fit(X)
    words = vec.get_feature_names_out()
    return [", ".join([words[i] for i in topic.argsort()[:-6:-1]]) for topic in lda.components_]

# --- Main Application ---
class EduSenseApp:
    def __init__(self):
        self.root = tb.Window(title="EduSense: Feedback & Analytics", themename="cosmo")
        self.root.geometry("1100x750")
        self.df = load_csv()
        self.filtered = self.df.copy()
        self.risk_clf = None

        try:
            self.ai_gen = pipeline("text-generation", model="distilgpt2")
        except:
            self.ai_gen = None

        self._build_menu()
        self.status = tb.Label(self.root, bootstyle="secondary", anchor=W)
        self.status.pack(side='bottom', fill='x')
        self._build_toolbar()

        self.nb = tb.Notebook(self.root)
        self.nb.pack(fill=BOTH, expand=1, padx=10, pady=10)

        self._build_data_tab()
        self._build_feedback_tab()
        self._build_analytics_tab()
        self._build_risk_tab()
        self._build_topics_tab()
        self._build_reports_tab()
        self._build_settings_tab()

        self.update_status("Ready.")

    def _build_menu(self):
        menubar = tk.Menu(self.root)
        filem = tk.Menu(menubar, tearoff=0)
        filem.add_command(label="Load CSV...", command=self._load_data)
        filem.add_command(label="Export Feedback CSV", command=self._export_feedback_csv)
        filem.add_separator()
        filem.add_command(label="Exit", command=self.root.destroy)
        menubar.add_cascade(label="File", menu=filem)
        self.root.config(menu=menubar)

    def _build_toolbar(self):
        tf = tb.Frame(self.root, padding=5)
        tf.pack(fill=X)
        tb.Button(tf, text="🔄 Reload", bootstyle="info", command=self._load_data).pack(side=LEFT, padx=3)
        tb.Button(tf, text="⚙️ Settings", bootstyle="warning", command=lambda: self.nb.select(6)).pack(side=LEFT, padx=3)

    def update_status(self, msg):
        self.status.config(text=msg)

    def _load_data(self):
        path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not path:
            return
        try:
            self.df = load_csv(path)
            self.filtered = self.df.copy()
            self._refresh_table()
            self.update_status(f"Loaded {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _build_data_tab(self):
        tab = tb.Frame(self.nb); self.nb.add(tab, text="Data")
        stats = tb.Frame(tab); stats.pack(fill=X, pady=5)
        total = len(self.df)
        avg_att = self.df["Attendance"].mean()
        avg_score = self.df[["Math","Science","English"]].mean().mean()
        for title, val in [("Students", total), ("Avg Attendance", f"{avg_att:.1f}%"), ("Avg Score", f"{avg_score:.1f}")]:
            card = tb.LabelFrame(stats, text=title, bootstyle="primary", width=200, height=80)
            card.pack(side=LEFT, expand=1, fill=BOTH, padx=5)
            lbl = tb.Label(card, text=str(val), font=("Helvetica", 20, "bold"))
            lbl.place(relx=0.5, rely=0.5, anchor=CENTER)

        fl = tb.Frame(tab); fl.pack(fill=X, pady=5)
        tb.Label(fl, text="🔍 Search:").pack(side=LEFT, padx=5)
        self.search_var = tk.StringVar()
        tb.Entry(fl, textvariable=self.search_var).pack(side=LEFT, fill=X, expand=1, padx=5)
        tb.Button(fl, text="Go", bootstyle="success-outline", command=self._apply_filter).pack(side=LEFT)

        tbl_frame = tb.Frame(tab)
        tbl_frame.pack(fill=BOTH, expand=1, padx=5, pady=5)
        vsb = tb.Scrollbar(tbl_frame, orient=VERTICAL)
        vsb.pack(side=RIGHT, fill=Y)
        self.tree = tb.Treeview(
            tbl_frame,
            columns=["Name","Math","Science","English","Attendance","Remarks"],
            show="headings", height=15,
            yscrollcommand=vsb.set
        )
        vsb.config(command=self.tree.yview)
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor=CENTER)
        self.tree.pack(fill=BOTH, expand=1)
        self._refresh_table()

    def _build_feedback_tab(self):
        tab = tb.Frame(self.nb); self.nb.add(tab, text="Feedback")
        panel = tb.Frame(tab); panel.pack(fill=X, pady=5)
        tb.Label(panel, text="👤 Student:").pack(side=LEFT, padx=5)
        self.sel_fb = tb.Combobox(panel, values=list(self.df['Name']), bootstyle="info")
        self.sel_fb.current(0); self.sel_fb.pack(side=LEFT, padx=5)
        tb.Button(panel, text="Show", bootstyle="secondary", command=self._show_feedback).pack(side=LEFT, padx=5)

        self.fb_text = tk.Text(tab, height=8)
        self.fb_text.pack(fill=X, padx=5, pady=5)

        btns = tb.Frame(tab); btns.pack(fill=X, pady=5)
        self.progress = tb.Progressbar(btns, mode="indeterminate")
        self.progress.pack(fill=X, expand=1, side=LEFT, padx=5)
        tb.Button(btns, text="AI Feedback", bootstyle="warning", command=self._gen_ai_fb).pack(side=LEFT, padx=3)
        tb.Button(btns, text="Save Manual", bootstyle="success", command=self._save_manual_fb).pack(side=LEFT, padx=3)
        tb.Button(btns, text="Export PDF", bootstyle="danger", command=self._export_feedback_pdf).pack(side=LEFT, padx=3)
        tb.Button(btns, text="Export CSV", bootstyle="primary", command=self._export_feedback_csv).pack(side=LEFT, padx=3)

    def _build_analytics_tab(self):
        tab = tb.Frame(self.nb); self.nb.add(tab, text="Analytics")
        avg = self.df[["Math","Science","English"]].mean()
        tb.Label(
            tab,
            text=f"Class Averages → Math:{avg['Math']:.1f}  Sci:{avg['Science']:.1f}  Eng:{avg['English']:.1f}",
            font=("Arial",12,"bold"), bootstyle="info"
        ).pack(pady=5)

        fig, ax = plt.subplots(figsize=(6,3))
        self.df[["Math","Science","English"]].mean().plot.bar(ax=ax, color=["#4e79a7","#f28e2b","#e15759"])
        ax.set_title("Subject Averages")
        FigureCanvasTkAgg(fig, master=tab).get_tk_widget().pack()

    def _build_risk_tab(self):
        tab = tb.Frame(self.nb); self.nb.add(tab, text="Risk")
        frm = tb.Frame(tab); frm.pack(pady=5)
        tb.Label(frm, text="Avg Threshold:").grid(row=0,column=0,padx=5)
        self.thresh_avg = tk.DoubleVar(value=65)
        tb.Entry(frm, textvariable=self.thresh_avg, width=6).grid(row=0,column=1)
        tb.Label(frm, text="Att Threshold:").grid(row=0,column=2,padx=5)
        self.thresh_att = tk.DoubleVar(value=75)
        tb.Entry(frm, textvariable=self.thresh_att, width=6).grid(row=0,column=3)
        tb.Button(frm, text="Train", bootstyle="warning", command=self._train_risk).grid(row=0,column=4,padx=5)
        tb.Button(frm, text="Flag At-Risk", bootstyle="danger", command=self._flag_risk).grid(row=0,column=5,padx=5)

        self.risk_list = tk.Listbox(tab, height=10)
        self.risk_list.pack(fill=BOTH, expand=1, padx=5, pady=5)

    def _build_topics_tab(self):
        tab = tb.Frame(self.nb); self.nb.add(tab, text="Topics")
        tb.Label(tab, text="Number of Topics:", bootstyle="info").pack(side=LEFT, padx=5, pady=5)
        self.topic_n = tk.IntVar(value=3)
        tb.Entry(tab, textvariable=self.topic_n, width=4).pack(side=LEFT)
        tb.Button(tab, text="Generate", bootstyle="success", command=self._gen_topics).pack(side=LEFT, padx=5)
        self.topics_box = tk.Text(tab, height=8)
        self.topics_box.pack(fill=BOTH, expand=1, padx=5, pady=5)

    def _build_reports_tab(self):
        tab = tb.Frame(self.nb); self.nb.add(tab, text="Reports")
        tb.Button(tab, text="Export All CSV", bootstyle="primary", command=self._export_feedback_csv).pack(pady=10)
        tb.Button(tab, text="Export All PDFs", bootstyle="secondary", command=self._export_all_pdfs).pack()

    def _build_settings_tab(self):
        tab = tb.Frame(self.nb); self.nb.add(tab, text="Settings")
        tb.Label(tab, text="Data File: " + DATA_FILE, bootstyle="info").pack(anchor=W, padx=5, pady=5)
        tb.Label(tab, text="Feedback Store: " + FEEDBACK_STORE, bootstyle="info").pack(anchor=W, padx=5)
        tb.Label(tab, text="Risk Model: " + RISK_MODEL_FILE, bootstyle="info").pack(anchor=W, padx=5)

    # Logic & Callbacks
    def _refresh_table(self):
        self.tree.delete(*self.tree.get_children())
        for _, r in self.filtered.iterrows():
            self.tree.insert(
                "", END,
                values=(r['Name'], r['Math'], r['Science'], r['English'], r['Attendance'], r.get('Remarks', ""))
            )
        self.update_status(f"{len(self.filtered)} records displayed.")

    def _apply_filter(self):
        q = self.search_var.get().lower()
        self.filtered = self.df[self.df['Name'].str.lower().str.contains(q)] if q else self.df.copy()
        self._refresh_table()

    def _show_feedback(self):
        name = self.sel_fb.get()
        ai = nlp_feedback(self.df[self.df['Name'] == name].iloc[0])['feedback']
        man = manual_feedback.get(name, "")
        self.fb_text.delete(1.0, END)
        self.fb_text.insert(END, f"AI: {ai}\nManual: {man}")
        self.update_status(f"Showing feedback for {name}")

    def _gen_ai_fb(self):
        if not self.ai_gen:
            messagebox.showwarning("AI Unavailable", "Model not loaded.")
            return
        name = self.sel_fb.get()
        row = self.df[self.df['Name'] == name].iloc[0]
        prompt = f"Student: {name}\nMath:{row['Math']},Sci:{row['Science']},Eng:{row['English']}\nConstructive feedback."
        self.progress.start()
        out = self.ai_gen(prompt, max_length=80)[0]['generated_text']
        self.progress.stop()
        manual_feedback[name] = out
        with open(FEEDBACK_STORE, "wb") as f:
            pickle.dump(manual_feedback, f)
        self._show_feedback()

    def _save_manual_fb(self):
        name = self.sel_fb.get()
        txt = self.fb_text.get(1.0, END).strip()
        manual_feedback[name] = txt
        with open(FEEDBACK_STORE, "wb") as f:
            pickle.dump(manual_feedback, f)
        self.update_status(f"Manual feedback for {name} saved.")

    def _export_feedback_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv")
        if not path:
            return
        df2 = self.df.copy()
        df2['Feedback'] = df2['Name'].apply(lambda n: manual_feedback.get(n, ""))
        save_csv(df2, path)
        self.update_status(f"Feedback CSV saved to {path}")

    def _export_feedback_pdf(self):
        path = filedialog.asksaveasfilename(defaultextension=".pdf")
        if not path:
            return
        fb = {n: manual_feedback.get(n, "") for n in self.df['Name']}
        save_pdf(fb, path)
        self.update_status(f"Feedback PDF saved to {path}")

    def _export_all_pdfs(self):
        folder = filedialog.askdirectory()
        if not folder:
            return
        for n in self.df['Name']:
            save_pdf({n: manual_feedback.get(n, "")}, os.path.join(folder, f"{n}.pdf"))
        self.update_status("All PDFs exported.")

    def _train_risk(self):
        self.risk_clf = train_risk_model(self.df, self.thresh_avg.get(), self.thresh_att.get())
        self.update_status("Risk model trained.")

    def _flag_risk(self):
        if not self.risk_clf:
            messagebox.showwarning("No Model", "Train model first.")
            return
        self.risk_list.delete(0, END)
        for _, r in self.df.iterrows():
            if predict_risk(r, self.risk_clf):
                self.risk_list.insert(END, r['Name'])
        self.update_status("At-risk students flagged.")

    def _gen_topics(self):
        docs = self.df['Remarks'].fillna("").tolist()
        topics = get_topics(docs, self.topic_n.get())
        self.topics_box.delete(1.0, END)
        for i, t in enumerate(topics, 1):
            self.topics_box.insert(END, f"Topic {i}: {t}\n")
        self.update_status(f"{len(topics)} topics generated.")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = EduSenseApp()
    app.run()
