from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy


import json
import datetime
from time import strftime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://iovivwytcukmgi:cdigSG1Zx3Ek_ANVRbSAN1r0db@ec2-174-129-197-200.compute-1.amazonaws.com:5432/d660ihttvdl1ls'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)
      

class Site(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    image_url = db.Column(db.String(200))
    description = db.Column(db.Text())

    def __init__(self, name, description):       
        self.name = name
        self.description = description 

    def __repr__(self):
        return '<Site name:%r>' % self.name

    def to_hash(self): 
        return {
            '_model_' : 'Site',
            'id': self.id, 
            'name' : self.name,
            'description' : self.description,
            'image_url' : self.image_url}

    def to_json(self):
        return json.dumps(self.to_hash())

class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    name = db.Column(db.String(80), unique=False)
    consent = db.Column(db.Text())
    password = db.Column(db.String(20))
    email = db.Column(db.String(80))
    created_at = db.Column(db.DateTime())
    modified_at = db.Column(db.DateTime())
    icon_url = db.Column(db.String(200))

    #notes = relationship("Note", order_by="Note.id", backref="account")

    def __init__(self, username):    	
        self.username = username 
        self.created_at = datetime.datetime.now()
        self.modified_at = datetime.datetime.now()
        self.icon_url = 'https://dl.dropboxusercontent.com/u/5104407/nntest/avatar.jpg'

    def __repr__(self):
        return '<Account username:%r>' % self.username

    def to_hash_short(self):
        return {'id': self.id, 'username': self.username}

    def to_hash(self): 
        return {
            '_model_' : 'Account',
            'id': self.id, 
            'username': self.username,
            'name' : self.name,
            'email' : self.email,
            'consent' : self.consent,
            'password' : self.password,
            'icon_url' : self.icon_url,
            'modified_at' : self.modified_at,
            'created_at' : self.created_at}        

    def to_json(self):
    	return jsonify(self.to_hash())


class Context(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kind = db.Column(db.String(40))
    name = db.Column(db.String(40))
    title = db.Column(db.Text())
    description = db.Column(db.Text())    
    extras = db.Column(db.Text())    
    site_id = db.Column(db.Integer, ForeignKey('site.id'))

    site = relationship("Site", backref=backref('contexts', order_by=id))

    def __init__(self, kind, name, title, description):               
        self.kind = kind
        self.name = name
        self.title = title
        self.description = description
        self.extras = ""

    def __repr__(self):
        return '<Context kind:%r, name:%r>' % (self.kind, self.name)

    def to_hash(self, format = 'full'):
        return {
            '_model_' : 'Context',
            'id': self.id, 'kind': self.kind, 'name' : self.name, 'title' : self.title,
            'description' : self.description, 'extras' : self.extras,
            'site' : self.site.to_hash()}            


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kind = db.Column(db.String(40), unique=False)
    content = db.Column(db.Text())
    created_at = db.Column(db.DateTime())
    modified_at = db.Column(db.DateTime())    

    longitude = db.Column(db.Float())
    latitude = db.Column(db.Float())

    account_id = db.Column(db.Integer, ForeignKey('account.id'))
    context_id = db.Column(db.Integer, ForeignKey('context.id'))

    account = relationship("Account", backref=backref('notes', order_by=id))
    context = relationship("Context", backref=backref('notes', order_by=id))

    def __init__(self, account_id, context_id, kind, content):       
        self.account_id = account_id
        self.context_id = context_id
        self.kind = kind
        self.content = content
        self.created_at = datetime.datetime.now()

    def __repr__(self):
        return '<Note kind:%r, content:%r>' % (self.kind, self.content)

    def to_hash(self, format = 'full'):
        h = {
            '_model_' : 'Note',
            'id': self.id, 
            'kind': self.kind, 
            'content' : self.content, 
            'created_at' : self.created_at,
            'modified_at' : self.modified_at,
            'latitude' : self.latitude,
            'longitude' : self.longitude}
        if format == 'full':
            h['medias'] = [ x.to_hash() for x in self.medias];
            h['context'] = self.context.to_hash();
            h['account'] = self.account.to_hash();
            feedbacks = Feedback.query.filter_by(table_name='Note', row_id=self.id).all()            
            h['feedbacks'] = [f.to_hash('short') for f in feedbacks]
            # h['feedbacks'] = [f.content for f in feedbacks]
        else:
            # h['medias'] = [ x.id for x in self.medias];
            h['context'] = self.context.id;
            h['account'] = self.account.id;
        return h
    
    def to_json(self):
        return json.dumps(self.to_hash())

class Media(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kind = db.Column(db.String(40))
    link = db.Column(db.Text())
    title = db.Column(db.Text())
    created_at = db.Column(db.DateTime())

    note_id = db.Column(db.Integer, ForeignKey('note.id'))

    note = relationship("Note", backref=backref('medias', order_by=id))

    def __init__(self, note_id, kind, title, link):       
        self.note_id = note_id
        self.kind = kind
        self.title = title
        self.link = link
        self.created_at = datetime.datetime.now()

    def __repr__(self):
        return '<Media title:%r>' % self.title

    def get_url(self):
        if self.kind == 'Photo':
            return "http://res.cloudinary.com/university-of-colorado/image/upload/v1400187706/" + self.link
        else:
            return "http://youtu.be/" + self.link

    def to_hash(self, format = 'full'):        
        #if format == 'full'
        return {
        '_model_' : 'Media',
        'id' : self.id, 
        'kind': self.kind, 
        'created_at' : self.created_at,
        'title' : self.title, 
        'link' : self.get_url()}

    def to_json(self):
        return json.dumps(self.to_hash())




class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, ForeignKey('account.id'))
    kind = db.Column(db.String(40))
    content = db.Column(db.Text())
    table_name = db.Column(db.String(20))
    row_id = db.Column(db.Integer)
    created_at = db.Column(db.DateTime())
    modified_at = db.Column(db.DateTime())

    account = relationship("Account", backref=backref('feedbacks', order_by=id))

    def __init__(self, account_id, kind, content, table_name, row_id):
        self.account_id = account_id
        self.row_id = row_id
        self.table_name = table_name
        self.kind = kind
        self.content = content
        self.created_at = datetime.datetime.now()
        self.modified_at = datetime.datetime.now()

    @staticmethod
    def resolve_target(table_name, row_id):
        #if table_name in ['Note', 'Context', 'Account']:
        if table_name.lower() == 'Note'.lower():
            return Note.query.get(row_id)
        elif table_name.lower() == 'Context'.lower():
            return Context.query.get(row_id)
        elif table_name.lower() == 'Account'.lower():
            return Account.query.get(row_id)
        elif table_name.lower() == 'Media'.lower():
            return Media.query.get(row_id)      
        else:
            return None        

    def __repr__(self):
        return '<Feedback by %s: %s on %s: %s >' % (self.account, self.kind, self.table_name, self.content)

    def resolve(self):
        return Feedback.resolve_target(self.table_name, self.row_id)

    def to_hash(self, format = 'full'):     
        h = {'id' : self.id,
                'kind' : self.kind, 'content': self.content,
                'created_at' : self.created_at,
                'modified_at' : self.modified_at,
                'account': self.account.to_hash()}
        if format == 'full':
            target = self.resolve()
            if target:
                target_hash = target.to_hash('short')
            else:
                target_hash = None
            h['target'] = {'model': self.table_name,
                           'id': self.row_id,
                           'data': target_hash}
        return h

        #     return {'id' : self.id,
        #         'kind' : self.kind, 'content': self.content,
        #         'created_at' : self.created_at,
        #         'modified_at' : self.modified_at,
        #         'account':};
        # elif format == 'short':
        #     return {'id' : self.id,
        #         'kind' : self.kind, 'content': self.content,
        #         'created_at' : self.created_at,
        #         'modified_at' : self.modified_at,
        #         'account': self.account.to_hash()};

