"""
Bước 3d — dò các bộ dữ liệu khác BẰNG TRUY VẤN, không phải đọc lướt.

LỖI CỦA TÔI Ở SCRIPT TRƯỚC: tôi đọc lướt và dừng ở 60.001 dòng, rồi in
"khong thay 31/2024/QH15". Các bộ đó có 150.000+ dòng. Nên câu đó KHÔNG có
nghĩa là "không có" — nó có nghĩa là "không có trong 40% đầu mà tôi chịu đọc".
Một cái giới hạn bị trình bày như một kết luận. Cùng loại lỗi với sắp xếp chuỗi.

Lần này dùng DuckDB truy vấn thẳng parquet qua hf:// — quét TOÀN BỘ, không cap.

HAI MỤC TIÊU:
  1. Tìm toàn văn Luật Đất đai 2024 (31/2024/QH15)
  2. QUAN TRỌNG HƠN: bộ doanhieung/vbpl có cột 'Phần hết hiệu lực' —
     tức PHẦN NÀO của văn bản đã hết hiệu lực. Nếu cột đó có dữ liệu thì nó
     thay thế được bảng article_status.csv ta phải dựng tay.

Chạy:  python src/probe_datasets.py
"""

import sys

BO = [
    ("doanhieung/vbpl", "Số ký hiệu", ["html_content", "markdown_content"]),
    ("vohuutridung/vietnamese-legal-documents", "document_number", ["content"]),
    ("minhdoan17/vietnamese-legal-documents", "document_number", ["content"]),
]
CAN_TIM = "31/2024/QH15"


def main():
    try:
        import duckdb
    except ImportError:
        print("Chay:  pip install duckdb")
        return 1

    con = duckdb.connect()
    con.execute("INSTALL httpfs; LOAD httpfs;")
    try:
        con.execute("INSTALL hf; LOAD hf;")
    except Exception:
        pass  # bản duckdb mới đã có sẵn hf://

    for ten, cot_so, cot_noi_dung in BO:
        print(f"\n{'='*66}\n{ten}\n{'='*66}")
        glob = f"hf://datasets/{ten}/**/*.parquet"
        try:
            n = con.execute(f"SELECT count(*) FROM read_parquet('{glob}')").fetchone()[0]
            print(f"  Tong so dong: {n:,}")
        except Exception as e:
            print(f"  KHONG DOC DUOC: {type(e).__name__}: {str(e)[:150]}")
            continue

        # --- Muc tieu 1: tim Luat Dat dai ---
        try:
            q = (f"SELECT * FROM read_parquet('{glob}') "
                 f'WHERE "{cot_so}" = \'{CAN_TIM}\' LIMIT 3')
            rows = con.execute(q).fetchdf()
            if len(rows) == 0:
                print(f"  [{CAN_TIM}] KHONG CO (da quet TOAN BO {n:,} dong)")
            else:
                print(f"  [{CAN_TIM}] TIM THAY {len(rows)} ban ghi")
                for c in cot_noi_dung:
                    if c in rows.columns:
                        v = rows.iloc[0][c]
                        print(f"      {c}: {len(str(v)):,} ky tu")
        except Exception as e:
            print(f"  loi truy van: {str(e)[:150]}")

        # --- Muc tieu 2: cot 'Phan het hieu luc' co du lieu khong? ---
        if ten == "doanhieung/vbpl":
            print("\n  --- KIEM TRA COT 'Phan het hieu luc' ---")
            try:
                q = (f"SELECT count(*) FILTER (WHERE \"Phần hết hiệu lực\" IS NOT NULL "
                     f"AND \"Phần hết hiệu lực\" <> '') AS co_du_lieu, count(*) AS tong "
                     f"FROM read_parquet('{glob}')")
                co, tong = con.execute(q).fetchone()
                print(f"      {co:,}/{tong:,} dong CO du lieu ({co/max(tong,1)*100:.1f}%)")
                if co:
                    q2 = (f"SELECT \"Số ký hiệu\", \"Phần hết hiệu lực\", \"Lí do hết hiệu lực\" "
                          f"FROM read_parquet('{glob}') "
                          f"WHERE \"Phần hết hiệu lực\" IS NOT NULL AND \"Phần hết hiệu lực\" <> '' "
                          f"LIMIT 5")
                    print("      VI DU:")
                    for sh, phan, ly_do in con.execute(q2).fetchall():
                        print(f"        {sh}")
                        print(f"          phan het hieu luc: {str(phan)[:160]}")
                        print(f"          ly do            : {str(ly_do)[:100]}")
            except Exception as e:
                print(f"      loi: {str(e)[:150]}")

            # Cot nay co du lieu cho Nghi dinh 126/2014 khong?
            print("\n  --- ND 126/2014 (ta biet D19-D50 da chet) ---")
            try:
                q3 = (f"SELECT \"Số ký hiệu\", \"Tình trạng hiệu lực\", \"Phần hết hiệu lực\", "
                      f"\"Lí do hết hiệu lực\", length(markdown_content) AS md_len "
                      f"FROM read_parquet('{glob}') WHERE \"Số ký hiệu\" = '126/2014/NĐ-CP'")
                for r in con.execute(q3).fetchall():
                    print(f"      so hieu   : {r[0]}")
                    print(f"      tinh trang: {r[1]}")
                    print(f"      PHAN HET  : {str(r[2])[:300]}")
                    print(f"      ly do     : {str(r[3])[:200]}")
                    print(f"      markdown  : {r[4]:,} ky tu" if r[4] else "      markdown  : trong")
            except Exception as e:
                print(f"      loi: {str(e)[:150]}")

    print("\nGui toan bo ket qua nay cho Claude.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
