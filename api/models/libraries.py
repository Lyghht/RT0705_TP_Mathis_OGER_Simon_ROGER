from extensions import db
from datetime import datetime
from sqlalchemy import CheckConstraint

class Library(db.Model):
    __tablename__ = 'libraries'

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    visibility = db.Column(db.String(20), nullable=False, default='private')
    
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("visibility IN ('public', 'private')", name='check_library_visibility'),
    )

    #Si on supprime la vidéothèque, on supprime tous les médias enfants
    medias = db.relationship('Media', backref='library', cascade="all, delete-orphan")

    def to_dict(self):
        """créer une vue pour l'api avec beaucoup d'informations"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'owner_id': self.owner_id,
            'visibility': self.visibility,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }