# import tkinter for GUI
import tkinter as tk
from tkinter import ttk, messagebox
# import all database functions
from queries import (
    get_categories,
    get_stylists_for_category,
    get_stylist_stats,
    get_services_for_stylist,
    get_stylist_services_details,
    get_stylist_reviews,
    get_client_by_phone,
    insert_client,
    get_stylist_service_ids,
    book_appointment_db,
    get_client_appointments,
    cancel_appointment_db,
    reschedule_appointment_db,
    get_completed_appointments_for_review,
    insert_review,
)

# main GUI class
class SalonGUI:
    def __init__(self, root):
        # setup main window
        self.root = root
        self.root.title('beauty salon booking system')
        self.root.geometry('1250x820')
        self.root.configure(bg='#f6efe8')

        # store selected items
        self.selected_appointment_id = None
        self.selected_stylist_id = None

        # variables for dropdowns
        self.category_var = tk.StringVar()
        self.stylist_var = tk.StringVar()
        self.service_var = tk.StringVar()
        self.review_var = tk.StringVar()
        self.rating_var = tk.StringVar()

        # setup style
        self.style = ttk.Style()
        try:
            self.style.theme_use('clam')
        except Exception:
            pass

        # setup UI parts
        self.setup_styles()
        self.setup_header()
        self.setup_tabs()
        self.setup_booking_tab()
        self.setup_history_tab()
        self.setup_review_tab()
        self.setup_table()
        self.load_categories()

    def setup_styles(self):
        # style settings for tabs and table
        self.style.configure('TNotebook', background='#f6efe8')
        self.style.configure('TNotebook.Tab', padding=(18, 10), font=('Arial', 10, 'bold'))
        self.style.configure('Treeview', rowheight=28, font=('Arial', 10))
        self.style.configure('Treeview.Heading', font=('Arial', 10, 'bold'))

    def setup_header(self):
        # create header bar
        header = tk.Frame(self.root, bg='#6f4e37', pady=12)
        header.pack(fill='x')
        # title text
        tk.Label(
            header,
            text='beauty salon booking system',
            bg='#6f4e37',
            fg='white',
            font=('Arial', 20, 'bold')
        ).pack()
        # subtitle text
        tk.Label(
            header,
            text='book, view, cancel, reschedule, and review appointments',
            bg='#6f4e37',
            fg='#f7e7d7',
            font=('Arial', 10)
        ).pack(pady=(3, 0))

    def setup_tabs(self):
        # create tabs
        self.tabs = ttk.Notebook(self.root)
        # create each tab
        self.tab_book = tk.Frame(self.tabs, bg='#f6efe8')
        self.tab_view = tk.Frame(self.tabs, bg='#f6efe8')
        self.tab_review = tk.Frame(self.tabs, bg='#f6efe8')

        self.tabs.add(self.tab_book, text='book appointment')
        self.tabs.add(self.tab_view, text='my appointments')
        self.tabs.add(self.tab_review, text='leave review')
        # display tabs
        self.tabs.pack(expand=1, fill='both', padx=10, pady=10)

    def setup_booking_tab(self):
        # section for choosing service
        top = tk.LabelFrame(self.tab_book, text='step 1: choose your service', bg='#f6efe8', padx=10, pady=10)
        top.pack(fill='x', padx=12, pady=8)

        # category dropdown
        self.category_box = ttk.Combobox(top, textvariable=self.category_var, state='readonly', width=22)
        self.category_box.grid(row=0, column=0, padx=8, pady=5)
        self.category_box.bind('<<ComboboxSelected>>', self.on_category_selected)

        # stylist dropdown
        self.stylist_box = ttk.Combobox(top, textvariable=self.stylist_var, state='readonly', width=25)
        self.stylist_box.grid(row=0, column=1, padx=8, pady=5)
        self.stylist_box.bind('<<ComboboxSelected>>', self.on_stylist_selected)

        # service dropdown
        self.service_box = ttk.Combobox(top, textvariable=self.service_var, state='readonly', width=25)
        self.service_box.grid(row=0, column=2, padx=8, pady=5)

        # button to view reviews
        tk.Button(
            top,
            text='view stylist reviews',
            bg='#a67b5b',
            fg='black',
            font=('Arial', 10, 'bold'),
            relief='flat',
            command=self.view_stylist_reviews
        ).grid(row=0, column=3, padx=8, pady=5)

        # client info section
        client = tk.LabelFrame(self.tab_book, text='step 2: enter client info', bg='#f6efe8', padx=10, pady=10)
        client.pack(fill='x', padx=12, pady=8)

        # entry fields
        self.first_name_entry = tk.Entry(client, width=22)
        self.last_name_entry = tk.Entry(client, width=22)
        self.phone_entry = tk.Entry(client, width=22)
        self.email_entry = tk.Entry(client, width=30)
        self.date_entry = tk.Entry(client, width=22)
        self.time_entry = tk.Entry(client, width=22)

        labels = [
            ('first name', 0, 0),
            ('last name', 0, 2),
            ('phone', 1, 0),
            ('email', 1, 2),
            ('date (yyyy-mm-dd)', 2, 0),
            ('time (hh:mm)', 2, 2),
        ]
        for text, row, col in labels:
            tk.Label(client, text=text, bg='#f6efe8').grid(row=row, column=col, sticky='w', padx=5, pady=5)

        self.first_name_entry.grid(row=0, column=1, padx=5, pady=5)
        self.last_name_entry.grid(row=0, column=3, padx=5, pady=5)
        self.phone_entry.grid(row=1, column=1, padx=5, pady=5)
        self.email_entry.grid(row=1, column=3, padx=5, pady=5)
        self.date_entry.grid(row=2, column=1, padx=5, pady=5)
        self.time_entry.grid(row=2, column=3, padx=5, pady=5)

        # button to book appointment
        tk.Button(
            self.tab_book,
            text='book appointment',
            bg='#6b8e23',
            fg='black',
            font=('Arial', 11, 'bold'),
            relief='flat',
            padx=18,
            pady=10,
            command=self.book_appointment,
        ).pack(pady=14)

    def setup_history_tab(self):
        # search section
        search_frame = tk.LabelFrame(self.tab_view, text='find my appointments', bg='#f6efe8', padx=10, pady=10)
        search_frame.pack(fill='x', padx=12, pady=8)

        tk.Label(search_frame, text='phone', bg='#f6efe8').grid(row=0, column=0, padx=5, pady=5)
        self.lookup_phone_entry = tk.Entry(search_frame, width=22)
        self.lookup_phone_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Button(
            search_frame,
            text='search',
            bg='#8b5e3c',
            fg='black',
            relief='flat',
            font=('Arial', 10, 'bold'),
            command=self.view_my_appointments,
        ).grid(row=0, column=2, padx=8, pady=5)

        # cancel/reschedule section
        action_frame = tk.LabelFrame(self.tab_view, text='cancel or reschedule selected appointment', bg='#f6efe8', padx=10, pady=10)
        action_frame.pack(fill='x', padx=12, pady=8)

        tk.Label(action_frame, text='new date (yyyy-mm-dd)', bg='#f6efe8').grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.reschedule_date_entry = tk.Entry(action_frame, width=20)
        self.reschedule_date_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(action_frame, text='new time (hh:mm)', bg='#f6efe8').grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.reschedule_time_entry = tk.Entry(action_frame, width=20)
        self.reschedule_time_entry.grid(row=0, column=3, padx=5, pady=5)

        tk.Button(
            action_frame,
            text='cancel appointment',
            bg='#c0392b',
            fg='black',
            relief='flat',
            font=('Arial', 10, 'bold'),
            padx=12,
            pady=8,
            command=self.cancel_appointment,
        ).grid(row=1, column=1, padx=8, pady=10)

        tk.Button(
            action_frame,
            text='reschedule appointment',
            bg='#d68910',
            fg='black',
            relief='flat',
            font=('Arial', 10, 'bold'),
            padx=12,
            pady=8,
            command=self.reschedule_appointment,
        ).grid(row=1, column=2, padx=8, pady=10)

        helper = tk.Label(
            self.tab_view,
            text='after you search, click one row in the table below before cancelling or rescheduling.',
            bg='#f6efe8',
            fg='#6f4e37',
            font=('Arial', 9, 'italic')
        )
        helper.pack(anchor='w', padx=18, pady=(0, 8))

    def setup_review_tab(self):
        # review section
        r_frame = tk.LabelFrame(self.tab_review, text='review a completed appointment', bg='#f6efe8', padx=10, pady=10)
        r_frame.pack(fill='x', padx=12, pady=8)

        tk.Label(r_frame, text='phone', bg='#f6efe8').grid(row=0, column=0, padx=5, pady=5)
        self.review_phone_entry = tk.Entry(r_frame, width=22)
        self.review_phone_entry.grid(row=0, column=1, padx=5, pady=5)

        # load completed appointments
        tk.Button(
            r_frame,
            text='load completed appointments',
            bg="#271a11",
            fg='black',
            relief='flat',
            font=('Arial', 10, 'bold'),
            command=self.load_completed_for_review,
        ).grid(row=0, column=2, padx=8, pady=5)

        self.review_box = ttk.Combobox(self.tab_review, textvariable=self.review_var, width=55, state='readonly')
        self.review_box.pack(pady=8)

        # rating dropdown
        tk.Label(self.tab_review, text='rating (1-5)', bg='#f6efe8').pack()
        self.rating_combo = ttk.Combobox(self.tab_review, textvariable=self.rating_var, values=['1', '2', '3', '4', '5'], width=8, state='readonly')
        self.rating_combo.pack(pady=5)

        # comment input
        tk.Label(self.tab_review, text='comment', bg='#f6efe8').pack()
        self.review_comment_entry = tk.Entry(self.tab_review, width=60)
        self.review_comment_entry.pack(pady=5)

        # submit review button
        tk.Button(
            self.tab_review,
            text='submit review',
            bg='#6b8e23',
            fg='black',
            relief='flat',
            font=('Arial', 10, 'bold'),
            padx=14,
            pady=8,
            command=self.submit_review,
        ).pack(pady=10)

    def setup_table(self):
        # table frame
        table_frame = tk.Frame(self.root, bg='#f6efe8')
        table_frame.pack(expand=True, fill='both', padx=12, pady=(0, 12))

        # table widget
        self.tree = ttk.Treeview(table_frame)
        self.tree.pack(side='left', expand=True, fill='both')
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)

        # scrollbar
        scroll = ttk.Scrollbar(table_frame, orient='vertical', command=self.tree.yview)
        scroll.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=scroll.set)

    def load_categories(self):
        # load categories from database
        categories = get_categories()
        self.category_box['values'] = categories
        self.category_box.set('select category')
        self.stylist_box.set('select stylist')
        self.service_box.set('select service')

    def on_category_selected(self, event=None):
        # load stylists after category is selected
        category = self.category_var.get()
        if category == 'select category':
            return

        stylists = get_stylists_for_category(category)
        self.stylist_box['values'] = stylists
        self.stylist_box.set('select stylist')
        self.service_box.set('select service')
        self.show_stylist_stats_in_table(category)

    def on_stylist_selected(self, event=None):
        # load stylist's services after stylist is selected
        stylist_name = self.stylist_var.get()
        category = self.category_var.get()
        if stylist_name == 'select stylist':
            return

        first, last = stylist_name.split(' ', 1)
        services = get_services_for_stylist(category, first, last)
        self.service_box['values'] = services
        self.service_box.set('select service')

        price_rows = get_stylist_services_details(first, last)
        self.show_table(['service name', 'duration (min)', 'price ($)', 'add-on'], price_rows)

    def show_stylist_stats_in_table(self, category):
        rows = get_stylist_stats(category)
        self.show_table(['stylist', 'avg rating', 'most booked service'], rows)

    def view_stylist_reviews(self):
        # show reviews for selected stylist
        stylist_name = self.stylist_var.get()
        if stylist_name in ['', 'select stylist']:
            messagebox.showwarning('warning', 'please select a stylist first.')
            return

        first, last = stylist_name.split(' ', 1)
        rows = get_stylist_reviews(first, last)

        review_win = tk.Toplevel(self.root)
        review_win.title(f'reviews: {stylist_name}')
        review_win.geometry('500x400')
        text_area = tk.Text(review_win, wrap='word', padx=10, pady=10)
        text_area.pack(expand=True, fill='both')

        if not rows:
            text_area.insert('1.0', 'no reviews yet.')
        else:
            for r in rows:
                text_area.insert('end', f'rating: {r[0]}/5 | {r[2]}\nreview: {r[1]}\n{'-' * 35}\n')

        text_area.config(state='disabled')

    def book_appointment(self):
        # user entered booking info 
        service_name = self.service_var.get().strip()
        stylist_name = self.stylist_var.get().strip()
        appt_date = self.date_entry.get().strip()
        appt_time = self.time_entry.get().strip()
        f_name = self.first_name_entry.get().strip()
        l_name = self.last_name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        email = self.email_entry.get().strip()

        if 'select' in service_name or 'select' in stylist_name or not appt_date or not appt_time or not phone:
            messagebox.showerror('error', 'please complete all booking fields.')
            return

        client_id = get_client_by_phone(phone)
        if not client_id:
            client_id = insert_client(f_name, l_name, phone, email)

        first, last = stylist_name.split(' ', 1)
        ids = get_stylist_service_ids(first, last, service_name)
        if not ids:
            messagebox.showerror('error', 'could not find the stylist and service you selected.')
            return

        stylist_id, service_id = ids
        success, msg = book_appointment_db(client_id, stylist_id, service_id, appt_date, appt_time)

        if success:
            messagebox.showinfo(
                'booking confirmation',
                f'appointment confirmed.\n\nclient: {f_name} {l_name}\nstylist: {stylist_name}\nservice: {service_name}\ndate: {appt_date}\ntime: {appt_time}'
            )
        else:
            messagebox.showerror('booking failed', msg)

    def view_my_appointments(self):
        # appointment lookup by phone number 
        phone = self.lookup_phone_entry.get().strip()
        if not phone:
            messagebox.showerror('error', 'please enter a phone number.')
            return

        rows = get_client_appointments(phone)
        if not rows:
            self.clear_table()
            messagebox.showinfo('no results', 'no appointments found for that phone number.')
            return

        self.show_table(
            ['appointment id', 'stylist', 'service', 'date', 'time', 'status', 'count with stylist', 'total client appts'],
            rows,
        )
        self.selected_appointment_id = None
        self.selected_stylist_id = None

    def on_tree_select(self, event=None):
        selected = self.tree.focus()
        if not selected:
            return

        values = self.tree.item(selected, 'values')
        if len(values) >= 8 and str(values[0]).isdigit():
            self.selected_appointment_id = int(values[0])
        else:
            self.selected_appointment_id = None

    def cancel_appointment(self):
        # cancel selected appointement
        if not self.selected_appointment_id:
            messagebox.showerror('error', 'select one appointment row first in the table.')
            return

        selected = self.tree.focus()
        values = self.tree.item(selected, 'values')
        current_status = str(values[5]).lower() if len(values) > 5 else ''

        if current_status != 'scheduled':
            messagebox.showerror('error', 'only scheduled appointments can be cancelled.')
            return

        success = cancel_appointment_db(self.selected_appointment_id)
        if success:
            messagebox.showinfo('success', 'appointment cancelled.')
            self.view_my_appointments()
        else:
            messagebox.showerror('error', 'cancel failed.')

    def reschedule_appointment(self):
        # reschedule appointment
        if not self.selected_appointment_id:
            messagebox.showerror('error', 'select one appointment row first in the table.')
            return

        new_date = self.reschedule_date_entry.get().strip()
        new_time = self.reschedule_time_entry.get().strip()
        if not new_date or not new_time:
            messagebox.showerror('error', 'enter a new date and new time.')
            return

        selected = self.tree.focus()
        values = self.tree.item(selected, 'values')
        current_status = str(values[5]).lower() if len(values) > 5 else ''
        if current_status != 'scheduled':
            messagebox.showerror('error', 'only scheduled appointments can be rescheduled.')
            return

        stylist_name = str(values[1])
        service_name = str(values[2])
        first, last = stylist_name.split(' ', 1)
        ids = get_stylist_service_ids(first, last, service_name)
        if not ids:
            messagebox.showerror('error', 'could not find the stylist for this appointment.')
            return

        stylist_id, _ = ids
        success, msg = reschedule_appointment_db(self.selected_appointment_id, stylist_id, new_date, new_time)
        if success:
            messagebox.showinfo('success', 'appointment rescheduled.')
            self.reschedule_date_entry.delete(0, 'end')
            self.reschedule_time_entry.delete(0, 'end')
            self.view_my_appointments()
        else:
            messagebox.showerror('error', msg)

    def load_completed_for_review(self):
        # load completed appointments, search for appointments by phone number 
        phone = self.review_phone_entry.get().strip()
        if not phone:
            messagebox.showerror('error', 'please enter a phone number.')
            return

        rows = get_completed_appointments_for_review(phone)
        if not rows:
            self.review_box['values'] = []
            self.review_box.set('')
            self.clear_table()
            messagebox.showinfo('no pending reviews', 'no completed appointments are ready for review.')
            return

        self.review_box['values'] = [f'{r[0]} - {r[1]} - {r[2]} - {r[3]}' for r in rows]
        self.review_box.set('select appointment to review')
        self.show_table(['appointment id', 'stylist', 'service', 'date'], rows)

    def submit_review(self):
        # submit a review for a completed appointment 
        selected = self.review_var.get().strip()
        rating = self.rating_var.get().strip()
        comment = self.review_comment_entry.get().strip()

        if not selected or 'select' in selected.lower():
            messagebox.showerror('error', 'please select an appointment.')
            return

        if not rating:
            messagebox.showerror('error', 'please choose a rating from 1 to 5.')
            return

        appt_id = selected.split(' - ')[0]
        if insert_review(appt_id, rating, comment):
            messagebox.showinfo('success', 'your review was submitted.')
            self.review_var.set('')
            self.rating_var.set('')
            self.review_comment_entry.delete(0, 'end')
            self.load_completed_for_review()
        else:
            messagebox.showerror('error', 'review submission failed.')

    def clear_table(self):
        # remove all rows from table
        for row in self.tree.get_children():
            self.tree.delete(row)

    def show_table(self, columns, rows):
        # display data in table 
        self.clear_table()
        self.tree['columns'] = columns
        self.tree['show'] = 'headings'

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=145, anchor='center')

        for row in rows:
            self.tree.insert('', 'end', values=row)


# main function to run the app
def main():
    root = tk.Tk()
    SalonGUI(root)
    root.mainloop()


#if __name__ == '__main__':
#    main()
