"""簡易 GUI：選擇 PDF，轉成保留圖片的 DOCX。"""

from __future__ import annotations

import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from converter import convert_pdf_to_docx


class Pdf2DocxApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("PDF → DOCX（保留圖片）")
        self.geometry("640x360")
        self.minsize(520, 300)

        self.pdf_var = tk.StringVar()
        self.out_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.status_var = tk.StringVar(value="請選擇 PDF 檔案")
        self._busy = False

        self._build_ui()

    def _build_ui(self) -> None:
        pad = {"padx": 12, "pady": 8}
        root = ttk.Frame(self, padding=12)
        root.pack(fill=tk.BOTH, expand=True)

        title = ttk.Label(root, text="PDF 轉 DOCX", font=("Segoe UI", 16, "bold"))
        title.pack(anchor=tk.W, **pad)

        hint = ttk.Label(
            root,
            text="會盡量保留文字、表格與內嵌圖片。掃描版 PDF（純圖片）也可轉出圖片頁。",
            wraplength=580,
        )
        hint.pack(anchor=tk.W, padx=12, pady=(0, 8))

        # PDF
        pdf_row = ttk.Frame(root)
        pdf_row.pack(fill=tk.X, **pad)
        ttk.Label(pdf_row, text="PDF：", width=10).pack(side=tk.LEFT)
        ttk.Entry(pdf_row, textvariable=self.pdf_var).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8)
        )
        ttk.Button(pdf_row, text="瀏覽…", command=self._pick_pdf).pack(side=tk.LEFT)

        # Output
        out_row = ttk.Frame(root)
        out_row.pack(fill=tk.X, **pad)
        ttk.Label(out_row, text="輸出：", width=10).pack(side=tk.LEFT)
        ttk.Entry(out_row, textvariable=self.out_var).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8)
        )
        ttk.Button(out_row, text="另存為…", command=self._pick_out).pack(side=tk.LEFT)

        # Password
        pw_row = ttk.Frame(root)
        pw_row.pack(fill=tk.X, **pad)
        ttk.Label(pw_row, text="密碼：", width=10).pack(side=tk.LEFT)
        ttk.Entry(pw_row, textvariable=self.password_var, show="*").pack(
            side=tk.LEFT, fill=tk.X, expand=True
        )
        ttk.Label(pw_row, text="（選填）").pack(side=tk.LEFT, padx=(8, 0))

        # Actions
        action = ttk.Frame(root)
        action.pack(fill=tk.X, **pad)
        self.convert_btn = ttk.Button(action, text="開始轉換", command=self._start_convert)
        self.convert_btn.pack(side=tk.LEFT)
        ttk.Button(action, text="結束", command=self.destroy).pack(side=tk.LEFT, padx=(8, 0))

        self.progress = ttk.Progressbar(root, mode="indeterminate")
        self.progress.pack(fill=tk.X, padx=12, pady=(4, 0))

        ttk.Label(root, textvariable=self.status_var).pack(anchor=tk.W, padx=12, pady=12)

    def _pick_pdf(self) -> None:
        path = filedialog.askopenfilename(
            title="選擇 PDF",
            filetypes=[("PDF 檔案", "*.pdf"), ("所有檔案", "*.*")],
        )
        if not path:
            return
        self.pdf_var.set(path)
        if not self.out_var.get().strip():
            self.out_var.set(str(Path(path).with_suffix(".docx")))
        self.status_var.set(f"已選擇：{Path(path).name}")

    def _pick_out(self) -> None:
        initial = self.out_var.get().strip() or self.pdf_var.get().strip()
        initial_name = Path(initial).stem + ".docx" if initial else "output.docx"
        path = filedialog.asksaveasfilename(
            title="儲存 DOCX",
            defaultextension=".docx",
            initialfile=initial_name,
            filetypes=[("Word 文件", "*.docx"), ("所有檔案", "*.*")],
        )
        if path:
            self.out_var.set(path)

    def _start_convert(self) -> None:
        if self._busy:
            return

        pdf = self.pdf_var.get().strip()
        if not pdf:
            messagebox.showwarning("提示", "請先選擇 PDF 檔案。")
            return
        if not Path(pdf).is_file():
            messagebox.showerror("錯誤", f"找不到檔案：\n{pdf}")
            return

        out = self.out_var.get().strip() or str(Path(pdf).with_suffix(".docx"))
        password = self.password_var.get() or None

        self._busy = True
        self.convert_btn.configure(state=tk.DISABLED)
        self.progress.start(12)
        self.status_var.set("轉換中，請稍候…")

        def worker() -> None:
            try:
                result = convert_pdf_to_docx(pdf, out, password=password)
            except Exception as exc:  # noqa: BLE001
                self.after(0, lambda: self._on_done(None, exc))
            else:
                self.after(0, lambda: self._on_done(result, None))

        threading.Thread(target=worker, daemon=True).start()

    def _on_done(self, result: Path | None, error: Exception | None) -> None:
        self.progress.stop()
        self.convert_btn.configure(state=tk.NORMAL)
        self._busy = False

        if error is not None:
            self.status_var.set("轉換失敗")
            messagebox.showerror("轉換失敗", str(error))
            return

        assert result is not None
        self.out_var.set(str(result))
        self.status_var.set(f"完成：{result}")
        messagebox.showinfo("完成", f"已輸出：\n{result}")


def main() -> None:
    app = Pdf2DocxApp()
    app.mainloop()


if __name__ == "__main__":
    main()
