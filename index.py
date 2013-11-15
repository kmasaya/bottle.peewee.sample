# coding: UTF-8
#!/usr/bin/python

from lib.bottle import get, post, request, run, template, static_file, redirect, html_escape
from lib import peewee

import os
import sys
import datetime

page_per_entry = 5
master_password = "password"


BASE_DIR = os.path.dirname( os.path.abspath( __file__))
STATIC_DIR = os.path.join( BASE_DIR, 'static')
db_filename = "./db.sqlite"

db = peewee.SqliteDatabase( db_filename)


class BaseModel( peewee.Model):
    class Meta:
        database = db

class EntryModel( BaseModel):
    title = peewee.CharField()
    body = peewee.TextField()
    name = peewee.CharField()
    password = peewee.CharField()
    created_at = peewee.DateTimeField()

    class Meta():
        order_by = ( "-created_at",)

def create_db():
    EntryModel.create_table()

def load_entries( page=1):
    entries = EntryModel.select().paginate( page, page_per_entry)

    return entries

def load_entry( entry_id):
    entry = EntryModel.select().where( EntryModel.id==entry_id)

    return entry

def save_entry( title, body, name, password="", entry_id=None):
    if entry_id is not  None:
        entry = load_entry( entry_id)
        entry.title = title
        entry.body = body
        entry.name = name
        entry.save()
    else:
        EntryModel.create( title=title, body=body, name=name, password=password, created_at=datetime.datetime.now())

def delete_entry( entry):
    entry.delete_instance()

def render( template_name="index", entries=[], page=1):
    entry_count = EntryModel.select().count()
    pages = int( float( entry_count) / page_per_entry + 0.5)
    return template( template_name, entries=entries, pages=pages, current_page=page)


@get( "")
@get( "/")
def index_view():
    entries = load_entries()

    return render( entries=entries, page=1)

@get( "/page/<paginate:int>/")
def page_view( paginate):
    entries = load_entries( paginate)

    return render( entries=entries, page=paginate)

@get( "/entry/<entryid:int>/")
def entry_view( entryid):
    entries = load_entry( entryid)

    return render( entries=entries, page=1)

@post( "/new/")
def new_view():
    title = request.forms.title
    body = request.forms.body
    name = request.forms.name
    password = request.forms.password

    save_entry( title, body, name, password)

    return redirect( "/")

@post( "/delete/")
def delete_view():
    entry_id = request.forms.entry_id
    password = request.forms.password

    entry = load_entry( entry_id)
    if entry[0].password == password or master_password == password:
        delete_entry( entry[0])

    return redirect( "/")

@get( "/static/<filename:path>")
def static_view( filename):
    return static_file( filename, root=STATIC_DIR)


if __name__ == "__main__":
    if not os.path.exists( db_filename):
        create_db()

    run( host="localhost")
