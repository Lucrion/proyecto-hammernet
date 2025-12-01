#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sqlite3

def main():
    root = os.path.dirname(os.path.dirname(__file__))
    db_path = os.path.join(root, 'ferreteria.db')
    if not os.path.exists(db_path):
        print('no_db')
        return
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute('PRAGMA table_info(ventas)')
    cols = [row[1] for row in cur.fetchall()]
    out = 'ventas_cols=' + ','.join(cols)
    print(out)
    with open(os.path.join(root, 'check_ventas_cols.out'), 'w', encoding='utf-8') as f:
        f.write(out+'\n')
    con.close()

if __name__ == '__main__':
    main()

