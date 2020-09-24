import tkinter as tk
from tkinter import filedialog
import pandas as pd
import numpy as np
import pymysql

import secret

from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity

if __name__ == '__main__':
    conn = pymysql.connect(
        host=secret.host,
        port=secret.port,
        password=secret.password,
        user=secret.user,
        db=secret.db
    )

    curs = conn.cursor()

    root = tk.Tk()
    root.withdraw()

    tasting_note_path = filedialog.askopenfilename()
    tasting_note = pd.read_csv(tasting_note_path, encoding="CP949")
    tasting_note_list = tasting_note.values

    for i, note in enumerate(tasting_note_list):
        get_bean = "SELECT bean_name FROM bean WHERE bean_name = '{}'".format(note[0])
        curs.execute(get_bean)

        row = curs.fetchone()

        if row:
            insert_sql = """
                        UPDATE bean SET tasting_note = '{}' WHERE bean_name = '{}'
                        """.format(note[1], note[0])

            curs.execute(insert_sql)
            conn.commit()

        else:
            insert_sql = """
            INSERT INTO bean (bean_name, tasting_note) VALUES ('{}', '{}')
            """.format(note[0], note[1])

            curs.execute(insert_sql)
            conn.commit()

        print(insert_sql)
