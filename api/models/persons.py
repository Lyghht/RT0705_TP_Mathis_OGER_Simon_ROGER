from extensions import db

class Person(db.Model):
    __tablename__ = 'persons'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    birthdate = db.Column(db.Date)

    def to_dict(self):
        """créer une vue pour l'api avec beaucoup d'informations"""
        return {
            'id': self.id,
            'name': self.name,
            'birthdate': self.birthdate.isoformat() if self.birthdate else None
        }

###########################################################################
###########################################################################
###########################################################################

class MediaPerson(db.Model):
    __tablename__ = 'media_persons'

    media_id = db.Column(db.Integer, db.ForeignKey('media.id', ondelete="CASCADE"), primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey('persons.id', ondelete="CASCADE"), primary_key=True)
    role = db.Column(db.String(50), primary_key=True) 
    
    character_name = db.Column(db.String(255))
    
    media = db.relationship('Media', backref=db.backref('cast', cascade="all, delete-orphan"))
    person = db.relationship('Person', backref=db.backref('filmography', cascade="all, delete-orphan"))

    def to_dict(self):
        """créer une vue pour l'api avec beaucoup d'informations"""
        return {
            'person_id': self.person_id,
            'person_name': self.person.name,
            'role': self.role,
            'character_name': self.character_name
        }