import sqlite3

conn=sqlite3.connect('cache.db')
c=conn.cursor()

def mark_email_processed(uid):
    c.execute("INSERT INTO emails VALUES (?)", (uid,))
    conn.commit()

def has_email_processed(uid):
    c.execute("SELECT * FROM emails WHERE uid=?", (uid,))
    return c.fetchone()

def prep():
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='emails'")
    if not c.fetchone():
        c.execute('''CREATE TABLE "emails" ("uid" INTEGER NOT NULL UNIQUE, PRIMARY KEY("UID"))''')
        conn.commit()

