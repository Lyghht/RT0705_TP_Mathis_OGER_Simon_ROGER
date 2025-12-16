from extensions import db
from datetime import datetime
from sqlalchemy import CheckConstraint

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    bio = db.Column(db.String(255))
    role = db.Column(db.String(20), nullable=False, default='user')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("role IN ('user', 'trusted', 'admin')", name='check_user_role'),
    )

    libraries = db.relationship('Library', backref='owner', lazy=True, cascade="all, delete-orphan")

    def to_dict(self, isAdmin=False):
        """créer une vue pour l'api avec beaucoup d'informations"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email if isAdmin else None,
            'bio': self.bio,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }