import customtkinter as ctk
from tkinter import messagebox, filedialog
import ticket as ticket_module


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

COLORS = {
    "bg_dark": "#1a1a2e",
    "bg_card": "#16213e",
    "bg_input": "#0f3460",
    "accent": "#e94560",
    "accent_hover": "#c73e54",
    "text": "#ffffff",
    "text_dim": "#a0a0b0",
    "success": "#00b894",
    "warning": "#fdcb6e",
    "danger": "#e94560",
    "info": "#0984e3",
    "border": "#2d3a5e",
}

PRIORITY_COLORS = {
    "Low": "#00b894",
    "Medium": "#fdcb6e",
    "High": "#e17055",
    "Critical": "#d63031",
}

STATUS_COLORS = {
    "Open": "#0984e3",
    "In Progress": "#fdcb6e",
    "Closed": "#00b894",
}


class HelpDeskApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("IT Help Desk Management System")
        self.geometry("1200x750")
        self.minsize(1000, 650)
        self.configure(fg_color=COLORS["bg_dark"])

        self.sidebar = self._create_sidebar()
        self.main_frame = self._create_main_area()
        self.current_frame = None
        self._show_dashboard()

    def _create_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color=COLORS["bg_card"])
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        logo_label = ctk.CTkLabel(
            sidebar, text="IT Help Desk", font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["accent"]
        )
        logo_label.pack(pady=(30, 5))

        subtitle = ctk.CTkLabel(
            sidebar, text="Management System", font=ctk.CTkFont(size=12),
            text_color=COLORS["text_dim"]
        )
        subtitle.pack(pady=(0, 30))

        separator = ctk.CTkFrame(sidebar, height=2, fg_color=COLORS["border"])
        separator.pack(fill="x", padx=20, pady=(0, 15))

        buttons_data = [
            ("Dashboard", self._show_dashboard),
            ("Create Ticket", self._show_create_ticket),
            ("View Tickets", self._show_view_tickets),
            ("Search Ticket", self._show_search_ticket),
            ("Close Ticket", self._show_close_ticket),
            ("Import Excel", self._import_excel),
            ("Export Excel", self._export_excel),
        ]

        self.sidebar_buttons = []
        for text, command in buttons_data:
            btn = ctk.CTkButton(
                sidebar, text=text, font=ctk.CTkFont(size=14),
                fg_color="transparent", text_color=COLORS["text"],
                hover_color=COLORS["bg_input"], anchor="w", height=40,
                corner_radius=8, command=command
            )
            btn.pack(fill="x", padx=15, pady=3)
            self.sidebar_buttons.append(btn)

        version_label = ctk.CTkLabel(
            sidebar, text="v1.0.0", font=ctk.CTkFont(size=10),
            text_color=COLORS["text_dim"]
        )
        version_label.pack(side="bottom", pady=15)

        return sidebar

    def _create_main_area(self):
        frame = ctk.CTkFrame(self, fg_color=COLORS["bg_dark"], corner_radius=0)
        frame.pack(side="right", fill="both", expand=True)
        return frame

    def _clear_main(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def _show_dashboard(self):
        self._clear_main()

        header = ctk.CTkLabel(
            self.main_frame, text="Dashboard", font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLORS["text"]
        )
        header.pack(anchor="w", padx=30, pady=(25, 20))

        tickets = ticket_module.get_all_tickets()
        total = len(tickets)
        open_count = sum(1 for t in tickets if t["status"] == "Open")
        in_progress = sum(1 for t in tickets if t["status"] == "In Progress")
        closed = sum(1 for t in tickets if t["status"] == "Closed")

        stats_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        stats_frame.pack(fill="x", padx=30, pady=(0, 20))

        stats = [
            ("Total Tickets", str(total), COLORS["info"]),
            ("Open", str(open_count), COLORS["warning"]),
            ("In Progress", str(in_progress), "#e17055"),
            ("Closed", str(closed), COLORS["success"]),
        ]

        for i, (label, value, color) in enumerate(stats):
            card = ctk.CTkFrame(stats_frame, fg_color=COLORS["bg_card"], corner_radius=12, height=120)
            card.grid(row=0, column=i, padx=(0, 15), sticky="nsew", pady=5)
            card.grid_propagate(False)
            stats_frame.grid_columnconfigure(i, weight=1)

            color_bar = ctk.CTkFrame(card, fg_color=color, corner_radius=12, height=5)
            color_bar.pack(fill="x", padx=15, pady=(15, 10))

            value_label = ctk.CTkLabel(
                card, text=value, font=ctk.CTkFont(size=36, weight="bold"),
                text_color=color
            )
            value_label.pack(pady=(5, 0))

            name_label = ctk.CTkLabel(
                card, text=label, font=ctk.CTkFont(size=13),
                text_color=COLORS["text_dim"]
            )
            name_label.pack(pady=(0, 10))

        recent_frame = ctk.CTkFrame(self.main_frame, fg_color=COLORS["bg_card"], corner_radius=12)
        recent_frame.pack(fill="both", expand=True, padx=30, pady=(0, 25))

        recent_label = ctk.CTkLabel(
            recent_frame, text="Recent Tickets", font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["text"]
        )
        recent_label.pack(anchor="w", padx=20, pady=(15, 10))

        if not tickets:
            empty_label = ctk.CTkLabel(
                recent_frame, text="No tickets yet. Create your first ticket!",
                font=ctk.CTkFont(size=14), text_color=COLORS["text_dim"]
            )
            empty_label.pack(pady=40)
        else:
            table_frame = ctk.CTkFrame(recent_frame, fg_color="transparent")
            table_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

            headers = ["ID", "Title", "Requester", "Department", "Priority", "Status"]
            header_widths = [60, 250, 150, 150, 100, 120]

            for i, (h, w) in enumerate(zip(headers, header_widths)):
                lbl = ctk.CTkLabel(
                    table_frame, text=h, font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=COLORS["accent"], width=w, anchor="w"
                )
                lbl.grid(row=0, column=i, padx=5, pady=(0, 8), sticky="w")

            separator = ctk.CTkFrame(table_frame, height=1, fg_color=COLORS["border"])
            separator.grid(row=1, column=0, columnspan=len(headers), sticky="ew", pady=(0, 5))

            display_tickets = tickets[:10]
            for row_idx, t in enumerate(display_tickets, start=2):
                row_data = [
                    str(t["id"]),
                    t["title"][:35] + ("..." if len(t["title"]) > 35 else ""),
                    t["requester"][:18] + ("..." if len(t["requester"]) > 18 else ""),
                    t["department"][:18] + ("..." if len(t["department"]) > 18 else ""),
                    t["priority"],
                    t["status"],
                ]

                for col_idx, (val, w) in enumerate(zip(row_data, header_widths)):
                    color = COLORS["text"]
                    if col_idx == 4:
                        color = PRIORITY_COLORS.get(val, COLORS["text"])
                    elif col_idx == 5:
                        color = STATUS_COLORS.get(val, COLORS["text"])

                    lbl = ctk.CTkLabel(
                        table_frame, text=val, font=ctk.CTkFont(size=12),
                        text_color=color, width=w, anchor="w"
                    )
                    lbl.grid(row=row_idx, column=col_idx, padx=5, pady=4, sticky="w")

    def _show_create_ticket(self):
        self._clear_main()

        header = ctk.CTkLabel(
            self.main_frame, text="Create New Ticket", font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLORS["text"]
        )
        header.pack(anchor="w", padx=30, pady=(25, 20))

        form_card = ctk.CTkFrame(self.main_frame, fg_color=COLORS["bg_card"], corner_radius=12)
        form_card.pack(fill="x", padx=30, pady=(0, 25))

        fields = {}

        row = 0
        ctk.CTkLabel(form_card, text="Title *", font=ctk.CTkFont(size=13, weight="bold"),
                      text_color=COLORS["text_dim"]).grid(row=row, column=0, sticky="w", padx=20, pady=(20, 5))
        fields["title"] = ctk.CTkEntry(form_card, placeholder_text="Enter ticket title", height=40,
                                        fg_color=COLORS["bg_input"], border_color=COLORS["border"], width=500)
        fields["title"].grid(row=row, column=1, padx=20, pady=(20, 5), sticky="w")

        row += 1
        ctk.CTkLabel(form_card, text="Description *", font=ctk.CTkFont(size=13, weight="bold"),
                      text_color=COLORS["text_dim"]).grid(row=row, column=0, sticky="nw", padx=20, pady=(10, 5))
        fields["description"] = ctk.CTkTextbox(form_card, height=120, fg_color=COLORS["bg_input"],
                                                border_color=COLORS["border"], width=500)
        fields["description"].grid(row=row, column=1, padx=20, pady=(10, 5), sticky="w")

        row += 1
        ctk.CTkLabel(form_card, text="Requester *", font=ctk.CTkFont(size=13, weight="bold"),
                      text_color=COLORS["text_dim"]).grid(row=row, column=0, sticky="w", padx=20, pady=(10, 5))
        fields["requester"] = ctk.CTkEntry(form_card, placeholder_text="Requester name", height=40,
                                            fg_color=COLORS["bg_input"], border_color=COLORS["border"], width=500)
        fields["requester"].grid(row=row, column=1, padx=20, pady=(10, 5), sticky="w")

        row += 1
        ctk.CTkLabel(form_card, text="Department *", font=ctk.CTkFont(size=13, weight="bold"),
                      text_color=COLORS["text_dim"]).grid(row=row, column=0, sticky="w", padx=20, pady=(10, 5))
        dept_options = ["IT", "HR", "Finance", "Marketing", "Operations", "Sales", "Engineering", "Other"]
        fields["department"] = ctk.CTkOptionMenu(form_card, values=dept_options, height=40,
                                                  fg_color=COLORS["bg_input"], button_color=COLORS["border"],
                                                  width=500)
        fields["department"].grid(row=row, column=1, padx=20, pady=(10, 5), sticky="w")
        fields["department"].set("IT")

        row += 1
        ctk.CTkLabel(form_card, text="Priority *", font=ctk.CTkFont(size=13, weight="bold"),
                      text_color=COLORS["text_dim"]).grid(row=row, column=0, sticky="w", padx=20, pady=(10, 5))
        priority_options = ["Low", "Medium", "High", "Critical"]
        fields["priority"] = ctk.CTkOptionMenu(form_card, values=priority_options, height=40,
                                                fg_color=COLORS["bg_input"], button_color=COLORS["border"],
                                                width=500)
        fields["priority"].grid(row=row, column=1, padx=20, pady=(10, 5), sticky="w")
        fields["priority"].set("Medium")

        row += 1
        ctk.CTkLabel(form_card, text="Assignee", font=ctk.CTkFont(size=13, weight="bold"),
                      text_color=COLORS["text_dim"]).grid(row=row, column=0, sticky="w", padx=20, pady=(10, 5))
        fields["assignee"] = ctk.CTkEntry(form_card, placeholder_text="Assignee name (optional)", height=40,
                                           fg_color=COLORS["bg_input"], border_color=COLORS["border"], width=500)
        fields["assignee"].grid(row=row, column=1, padx=20, pady=(10, 5), sticky="w")

        row += 1
        btn_frame = ctk.CTkFrame(form_card, fg_color="transparent")
        btn_frame.grid(row=row, column=1, padx=20, pady=(20, 25), sticky="w")

        def submit():
            desc_text = fields["description"].get("1.0", "end").strip()
            ticket_module.create_ticket(
                fields["title"].get(),
                desc_text,
                fields["requester"].get(),
                fields["department"].get(),
                fields["priority"].get(),
                fields["assignee"].get()
            )
            self._show_dashboard()

        ctk.CTkButton(
            btn_frame, text="Create Ticket", font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            height=42, width=160, corner_radius=8, command=submit
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            btn_frame, text="Cancel", font=ctk.CTkFont(size=14),
            fg_color=COLORS["border"], hover_color=COLORS["bg_input"],
            height=42, width=120, corner_radius=8, command=self._show_dashboard
        ).pack(side="left")

    def _show_view_tickets(self):
        self._clear_main()

        header = ctk.CTkLabel(
            self.main_frame, text="All Tickets", font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLORS["text"]
        )
        header.pack(anchor="w", padx=30, pady=(25, 20))

        filter_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        filter_frame.pack(fill="x", padx=30, pady=(0, 15))

        self._status_filter_var = ctk.StringVar(value="All")
        ctk.CTkLabel(filter_frame, text="Status:", font=ctk.CTkFont(size=13),
                      text_color=COLORS["text_dim"]).pack(side="left", padx=(0, 8))
        status_menu = ctk.CTkOptionMenu(
            filter_frame, variable=self._status_filter_var,
            values=["All", "Open", "In Progress", "Closed"], width=140, height=35,
            fg_color=COLORS["bg_input"], button_color=COLORS["border"],
            command=lambda _: self._refresh_tickets_table()
        )
        status_menu.pack(side="left", padx=(0, 15))

        self._priority_filter_var = ctk.StringVar(value="All")
        ctk.CTkLabel(filter_frame, text="Priority:", font=ctk.CTkFont(size=13),
                      text_color=COLORS["text_dim"]).pack(side="left", padx=(0, 8))
        priority_menu = ctk.CTkOptionMenu(
            filter_frame, variable=self._priority_filter_var,
            values=["All", "Low", "Medium", "High", "Critical"], width=140, height=35,
            fg_color=COLORS["bg_input"], button_color=COLORS["border"],
            command=lambda _: self._refresh_tickets_table()
        )
        priority_menu.pack(side="left")

        table_outer = ctk.CTkFrame(self.main_frame, fg_color=COLORS["bg_card"], corner_radius=12)
        table_outer.pack(fill="both", expand=True, padx=30, pady=(0, 25))

        headers = ["ID", "Title", "Requester", "Dept", "Priority", "Status", "Assignee", "Created"]
        col_widths = [50, 220, 120, 100, 80, 100, 120, 150]

        header_frame = ctk.CTkFrame(table_outer, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=(15, 5))

        for h, w in zip(headers, col_widths):
            ctk.CTkLabel(header_frame, text=h, font=ctk.CTkFont(size=11, weight="bold"),
                          text_color=COLORS["accent"], width=w, anchor="w").pack(side="left", padx=3)

        sep = ctk.CTkFrame(table_outer, height=1, fg_color=COLORS["border"])
        sep.pack(fill="x", padx=15, pady=(5, 0))

        scroll_frame = ctk.CTkScrollableFrame(table_outer, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=15, pady=(5, 15))
        self._tickets_scroll = scroll_frame
        self._tickets_headers = headers
        self._tickets_col_widths = col_widths
        self._refresh_tickets_table()

    def _refresh_tickets_table(self):
        if not hasattr(self, "_tickets_scroll"):
            return
        for widget in self._tickets_scroll.winfo_children():
            widget.destroy()

        tickets = ticket_module.get_all_tickets()

        status_filter = self._status_filter_var.get()
        priority_filter = self._priority_filter_var.get()
        if status_filter != "All":
            tickets = [t for t in tickets if t["status"] == status_filter]
        if priority_filter != "All":
            tickets = [t for t in tickets if t["priority"] == priority_filter]

        if not tickets:
            ctk.CTkLabel(self._tickets_scroll, text="No tickets found.",
                          font=ctk.CTkFont(size=14), text_color=COLORS["text_dim"]).pack(pady=30)
            return

        for t in tickets:
            row_frame = ctk.CTkFrame(self._tickets_scroll, fg_color=COLORS["bg_input"], corner_radius=6, height=38)
            row_frame.pack(fill="x", pady=2)
            row_frame.pack_propagate(False)

            created = t["created_at"][:10] if t["created_at"] else ""
            row_data = [
                str(t["id"]),
                t["title"][:30] + ("..." if len(t["title"]) > 30 else ""),
                t["requester"][:15] + ("..." if len(t["requester"]) > 15 else ""),
                t["department"][:12] + ("..." if len(t["department"]) > 12 else ""),
                t["priority"],
                t["status"],
                t["assignee"][:15] + ("..." if len(t["assignee"]) > 15 else "") if t["assignee"] else "-",
                created,
            ]

            for val, w in zip(row_data, self._tickets_col_widths):
                color = COLORS["text"]
                if val in PRIORITY_COLORS:
                    color = PRIORITY_COLORS[val]
                elif val in STATUS_COLORS:
                    color = STATUS_COLORS[val]

                ctk.CTkLabel(row_frame, text=val, font=ctk.CTkFont(size=11),
                              text_color=color, width=w, anchor="w").pack(side="left", padx=3)

    def _show_search_ticket(self):
        self._clear_main()

        header = ctk.CTkLabel(
            self.main_frame, text="Search Tickets", font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLORS["text"]
        )
        header.pack(anchor="w", padx=30, pady=(25, 20))

        search_card = ctk.CTkFrame(self.main_frame, fg_color=COLORS["bg_card"], corner_radius=12)
        search_card.pack(fill="x", padx=30, pady=(0, 15))

        search_row = ctk.CTkFrame(search_card, fg_color="transparent")
        search_row.pack(fill="x", padx=20, pady=20)

        self._search_entry = ctk.CTkEntry(
            search_row, placeholder_text="Search by title, description, requester, department...",
            height=42, fg_color=COLORS["bg_input"], border_color=COLORS["border"], width=500
        )
        self._search_entry.pack(side="left", padx=(0, 10))
        self._search_entry.bind("<Return>", lambda _: self._do_search())

        ctk.CTkButton(
            search_row, text="Search", font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            height=42, width=120, corner_radius=8, command=self._do_search
        ).pack(side="left")

        self._search_results_frame = ctk.CTkFrame(self.main_frame, fg_color=COLORS["bg_card"], corner_radius=12)
        self._search_results_frame.pack(fill="both", expand=True, padx=30, pady=(0, 25))

    def _do_search(self):
        query = self._search_entry.get().strip()
        for widget in self._search_results_frame.winfo_children():
            widget.destroy()

        results = ticket_module.search_tickets(query)

        count_label = ctk.CTkLabel(
            self._search_results_frame,
            text=f"Found {len(results)} result(s)" if query else "Enter a search term",
            font=ctk.CTkFont(size=13), text_color=COLORS["text_dim"]
        )
        count_label.pack(anchor="w", padx=20, pady=(15, 10))

        if not results:
            ctk.CTkLabel(self._search_results_frame, text="No results found.",
                          font=ctk.CTkFont(size=14), text_color=COLORS["text_dim"]).pack(pady=20)
            return

        scroll = ctk.CTkScrollableFrame(self._search_results_frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        headers = ["ID", "Title", "Requester", "Priority", "Status"]
        col_widths = [50, 250, 150, 100, 100]

        for h, w in zip(headers, col_widths):
            ctk.CTkLabel(scroll, text=h, font=ctk.CTkFont(size=11, weight="bold"),
                          text_color=COLORS["accent"], width=w, anchor="w").pack(side="left", padx=3)

        sep = ctk.CTkFrame(scroll, height=1, fg_color=COLORS["border"])
        sep.pack(fill="x", pady=(5, 8))

        for t in results:
            row_frame = ctk.CTkFrame(scroll, fg_color=COLORS["bg_input"], corner_radius=6, height=36)
            row_frame.pack(fill="x", pady=2)
            row_frame.pack_propagate(False)

            row_data = [str(t["id"]), t["title"][:35], t["requester"], t["priority"], t["status"]]
            for val, w in zip(row_data, col_widths):
                color = COLORS["text"]
                if val in PRIORITY_COLORS:
                    color = PRIORITY_COLORS[val]
                elif val in STATUS_COLORS:
                    color = STATUS_COLORS[val]
                ctk.CTkLabel(row_frame, text=val, font=ctk.CTkFont(size=11),
                              text_color=color, width=w, anchor="w").pack(side="left", padx=3)

    def _show_close_ticket(self):
        self._clear_main()

        header = ctk.CTkLabel(
            self.main_frame, text="Close Ticket", font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLORS["text"]
        )
        header.pack(anchor="w", padx=30, pady=(25, 20))

        card = ctk.CTkFrame(self.main_frame, fg_color=COLORS["bg_card"], corner_radius=12)
        card.pack(fill="x", padx=30, pady=(0, 25))

        ctk.CTkLabel(card, text="Enter the Ticket ID to close:", font=ctk.CTkFont(size=14),
                      text_color=COLORS["text"]).pack(anchor="w", padx=20, pady=(20, 10))

        id_entry = ctk.CTkEntry(card, placeholder_text="Ticket ID", height=40, width=300,
                                 fg_color=COLORS["bg_input"], border_color=COLORS["border"])
        id_entry.pack(anchor="w", padx=20, pady=(0, 10))

        ticket_info_label = ctk.CTkLabel(card, text="", font=ctk.CTkFont(size=13),
                                          text_color=COLORS["text_dim"])
        ticket_info_label.pack(anchor="w", padx=20, pady=(0, 10))

        def lookup_ticket():
            tid = id_entry.get().strip()
            if not tid.isdigit():
                ticket_info_label.configure(text="Please enter a valid numeric ID.", text_color=COLORS["danger"])
                return
            t = ticket_module.get_ticket_by_id(int(tid))
            if not t:
                ticket_info_label.configure(text="Ticket not found.", text_color=COLORS["danger"])
                return
            ticket_info_label.configure(
                text=f"#{t['id']} | {t['title']} | Status: {t['status']} | Priority: {t['priority']}",
                text_color=COLORS["text"]
            )

        def do_close():
            tid = id_entry.get().strip()
            if not tid.isdigit():
                messagebox.showwarning("Warning", "Please enter a valid numeric ID.")
                return
            result = ticket_module.close_ticket(int(tid))
            if result:
                self._show_close_ticket()

        ctk.CTkButton(card, text="Look Up", font=ctk.CTkFont(size=13),
                       fg_color=COLORS["info"], hover_color="#0770c7",
                       height=38, width=120, corner_radius=8, command=lookup_ticket
                       ).pack(anchor="w", padx=20, pady=(0, 5))

        btn_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_row.pack(anchor="w", padx=20, pady=(5, 25))

        ctk.CTkButton(
            btn_row, text="Close Ticket", font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS["danger"], hover_color="#c73750",
            height=42, width=140, corner_radius=8, command=do_close
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            btn_row, text="Back to Dashboard", font=ctk.CTkFont(size=14),
            fg_color=COLORS["border"], hover_color=COLORS["bg_input"],
            height=42, width=160, corner_radius=8, command=self._show_dashboard
        ).pack(side="left")

    def _import_excel(self):
        filepath = filedialog.askopenfilename(
            title="Import Tickets from Excel",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        if filepath:
            count = ticket_module.import_tickets_from_excel(filepath)
            if count > 0:
                self._show_dashboard()

    def _export_excel(self):
        filepath = filedialog.asksaveasfilename(
            title="Export Tickets to Excel",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        if filepath:
            ticket_module.export_tickets_to_excel(filepath)
