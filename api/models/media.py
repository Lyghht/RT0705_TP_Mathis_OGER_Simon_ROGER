from extensions import db
from datetime import datetime
from sqlalchemy import CheckConstraint

class Franchise(db.Model):
    __tablename__ = 'franchises'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)

    medias = db.relationship('Media', backref='franchise', lazy=True)

    def to_dict(self):
        """créer une vue pour l'api avec beaucoup d'informations"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }

###########################################################################
###########################################################################
###########################################################################

class Genre(db.Model):
    __tablename__ = 'genres'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

    def to_dict(self):
        """créer une vue pour l'api avec beaucoup d'informations"""
        return {
            'id': self.id,
            'name': self.name
        }

###########################################################################
###########################################################################
###########################################################################

class Media(db.Model):
    __tablename__ = 'media'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    
    type = db.Column(db.String(50), nullable=False)
    release_year = db.Column(db.SmallInteger)
    duration = db.Column(db.Time)
    synopsis = db.Column(db.Text)
    cover_image_url = db.Column(db.String)
    trailer_url = db.Column(db.String)
    
    library_id = db.Column(db.Integer, db.ForeignKey('libraries.id', ondelete="CASCADE"), nullable=False)
    franchise_id = db.Column(db.Integer, db.ForeignKey('franchises.id'))
    franchise_order = db.Column(db.Integer)
    visibility = db.Column(db.String(20), nullable=False)
    
    __table_args__ = (
        CheckConstraint(type.in_(['film', 'serie']), name='check_media_type'),
        CheckConstraint(visibility.in_(['public', 'private']), name='check_media_visibility'),
    )
    
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    genres = db.relationship('Genre', secondary='media_genres', backref='medias')

    def to_dict(self):
        """créer une vue pour l'api avec beaucoup d'informations"""
        return {
            'id': self.id,
            'title': self.title,
            'type': self.type,
            'release_year': self.release_year,
            'duration': str(self.duration) if self.duration else None,
            'synopsis': self.synopsis,
            'cover_image_url': self.cover_image_url,
            'trailer_url': self.trailer_url,
            'library_id': self.library_id,
            'franchise_id': self.franchise_id,
            'franchise_order': self.franchise_order,
            'owner_id': self.library.owner_id,
            'owner_name': self.library.owner.username,
            'visibility': self.visibility,
            'genres': [g.to_dict() for g in self.genres],
            'persons': [mp.to_dict() for mp in self.cast],
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def to_dict_summary(self):
        """créer une vue plus légère pour les listes/recherches"""
        return {
            'id': self.id,
            'title': self.title,
            'type': self.type,
            'duration': str(self.duration) if self.duration else None,
            'release_year': self.release_year,
            'synopsis': self.synopsis,
            'cover_image_url': self.cover_image_url,
            'library_id': self.library_id,
            'visibility': self.visibility,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

###########################################################################
###########################################################################
###########################################################################


#TABLE DE LIAISON MEDIA <-> GENRES
class MediaGenre(db.Model):
    __tablename__ = 'media_genres'
    
    media_id = db.Column(db.Integer, db.ForeignKey('media.id', ondelete="CASCADE"), primary_key=True)
    genre_id = db.Column(db.Integer, db.ForeignKey('genres.id', ondelete="CASCADE"), primary_key=True)