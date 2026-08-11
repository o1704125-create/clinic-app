
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window

import sqlite3
from datetime import datetime


DB = "clinic_app/clinic.db"


def database():
    return sqlite3.connect(DB)


def today():
    return datetime.now().strftime("%Y-%m-%d")


class HomeScreen(Screen):

    def on_pre_enter(self):
        self.update_dashboard()

    def update_dashboard(self):

        db = database()
        cursor = db.cursor()

        cursor.execute(
            "SELECT COALESCE(SUM(amount),0) FROM patients WHERE date=?",
            (today(),)
        )
        revenue = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COALESCE(SUM(amount),0) FROM expenses WHERE date=?",
            (today(),)
        )
        expenses = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(*) FROM patients WHERE date=?",
            (today(),)
        )
        patients = cursor.fetchone()[0]

        db.close()

        self.revenue.text = f"إيراد اليوم\n{revenue:,.0f}"
        self.expenses.text = f"المصروفات\n{expenses:,.0f}"
        self.net.text = f"الصافي\n{revenue-expenses:,.0f}"
        self.patients.text = f"عدد المرضى\n{patients}"


class PatientScreen(Screen):

    def add_patient(self):

        name = self.name.text.strip()
        age = self.age.text.strip()
        address = self.address.text.strip()
        service = self.service.text.strip()
        amount = self.amount.text.strip()

        if not name or not amount:
            self.status.text = "أدخل الاسم والمبلغ"
            return

        try:
            age = int(age) if age else 0
            amount = float(amount)
        except ValueError:
            self.status.text = "العمر والمبلغ يجب أن يكونا أرقاماً"
            return

        db = database()

        db.execute("""
            INSERT INTO patients
            (name, age, address, service, amount, date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            name,
            age,
            address,
            service,
            amount,
            today()
        ))

        db.commit()
        db.close()

        self.name.text = ""
        self.age.text = ""
        self.address.text = ""
        self.service.text = ""
        self.amount.text = ""

        self.status.text = "تم تسجيل المريض بنجاح ✅"


class ExpenseScreen(Screen):

    def add_expense(self):

        description = self.description.text.strip()
        amount = self.amount.text.strip()

        if not description or not amount:
            self.status.text = "أدخل وصف المصروف والمبلغ"
            return

        try:
            amount = float(amount)
        except ValueError:
            self.status.text = "المبلغ يجب أن يكون رقماً"
            return

        db = database()

        db.execute("""
            INSERT INTO expenses
            (description, amount, date)
            VALUES (?, ?, ?)
        """, (
            description,
            amount,
            today()
        ))

        db.commit()
        db.close()

        self.description.text = ""
        self.amount.text = ""

        self.status.text = "تم تسجيل المصروف ✅"


class ClinicApp(App):

    def build(self):

        manager = ScreenManager()

        # =========================
        # الرئيسية
        # =========================

        home = HomeScreen(name="home")

        layout = BoxLayout(
            orientation="vertical",
            padding=20,
            spacing=15
        )

        title = Label(
            text="نظام إدارة العيادة",
            font_size=28,
            size_hint_y=None,
            height=60
        )

        layout.add_widget(title)

        home.revenue = Label(
            text="إيراد اليوم\n0",
            font_size=22
        )

        home.expenses = Label(
            text="المصروفات\n0",
            font_size=22
        )

        home.net = Label(
            text="الصافي\n0",
            font_size=22
        )

        home.patients = Label(
            text="عدد المرضى\n0",
            font_size=22
        )

        layout.add_widget(home.revenue)
        layout.add_widget(home.expenses)
        layout.add_widget(home.net)
        layout.add_widget(home.patients)

        patient_button = Button(
            text="تسجيل مريض",
            size_hint_y=None,
            height=55
        )

        patient_button.bind(
            on_press=lambda x: setattr(
                manager,
                "current",
                "patients"
            )
        )

        expense_button = Button(
            text="المصروفات",
            size_hint_y=None,
            height=55
        )

        expense_button.bind(
            on_press=lambda x: setattr(
                manager,
                "current",
                "expenses"
            )
        )

        layout.add_widget(patient_button)
        layout.add_widget(expense_button)

        home.add_widget(layout)

        # =========================
        # تسجيل المريض
        # =========================

        patient = PatientScreen(name="patients")

        p = GridLayout(
            cols=1,
            padding=20,
            spacing=10
        )

        patient.name = TextInput(
            hint_text="اسم المريض",
            multiline=False
        )

        patient.age = TextInput(
            hint_text="العمر",
            multiline=False,
            input_filter="int"
        )

        patient.address = TextInput(
            hint_text="السكن",
            multiline=False
        )

        patient.service = TextInput(
            hint_text="نوع الخدمة / الكشف",
            multiline=False
        )

        patient.amount = TextInput(
            hint_text="المبلغ المدفوع",
            multiline=False,
            input_filter="float"
        )

        p.add_widget(
            Label(
                text="تسجيل مريض",
                font_size=25
            )
        )

        p.add_widget(patient.name)
        p.add_widget(patient.age)
        p.add_widget(patient.address)
        p.add_widget(patient.service)
        p.add_widget(patient.amount)

        save_patient = Button(
            text="حفظ المريض",
            size_hint_y=None,
            height=55
        )

        save_patient.bind(
            on_press=lambda x: patient.add_patient()
        )

        p.add_widget(save_patient)

        patient.status = Label(
            text="",
            size_hint_y=None,
            height=40
        )

        p.add_widget(patient.status)

        back = Button(
            text="رجوع",
            size_hint_y=None,
            height=50
        )

        back.bind(
            on_press=lambda x: setattr(
                manager,
                "current",
                "home"
            )
        )

        p.add_widget(back)

        patient.add_widget(p)

        # =========================
        # المصروفات
        # =========================

        expense = ExpenseScreen(name="expenses")

        e = GridLayout(
            cols=1,
            padding=20,
            spacing=10
        )

        expense.description = TextInput(
            hint_text="وصف المصروف",
            multiline=False
        )

        expense.amount = TextInput(
            hint_text="المبلغ",
            multiline=False,
            input_filter="float"
        )

        e.add_widget(
            Label(
                text="إضافة مصروف",
                font_size=25
            )
        )

        e.add_widget(expense.description)
        e.add_widget(expense.amount)

        save_expense = Button(
            text="حفظ المصروف",
            size_hint_y=None,
            height=55
        )

        save_expense.bind(
            on_press=lambda x: expense.add_expense()
        )

        e.add_widget(save_expense)

        expense.status = Label(
            text="",
            size_hint_y=None,
            height=40
        )

        e.add_widget(expense.status)

        back2 = Button(
            text="رجوع",
            size_hint_y=None,
            height=50
        )

        back2.bind(
            on_press=lambda x: setattr(
                manager,
                "current",
                "home"
            )
        )

        e.add_widget(back2)

        expense.add_widget(e)

        manager.add_widget(home)
        manager.add_widget(patient)
        manager.add_widget(expense)

        return manager


if __name__ == "__main__":
    ClinicApp().run()
