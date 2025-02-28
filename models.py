"""
This module defines the database models for the containers plugin in CTFd.
"""

from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from CTFd.models import db
from CTFd.models import Challenges

class ContainerChallengeModel(Challenges):
    """
    Represents a container-based challenge in CTFd.
    """
    __mapper_args__ = {"polymorphic_identity": "container"}
    id = db.Column(
        db.Integer, db.ForeignKey("challenges.id", ondelete="CASCADE"), primary_key=True
    )
    image = db.Column(db.Text)
    # Keep old port column for backward compatibility
    port = db.Column(db.Integer, nullable=True)
    port_range_start = db.Column(db.Integer, nullable=True)
    port_range_end = db.Column(db.Integer, nullable=True)
    command = db.Column(db.Text, default="")
    volumes = db.Column(db.Text, default="")

    initial = db.Column(db.Integer, default=0)
    minimum = db.Column(db.Integer, default=0)
    decay = db.Column(db.Integer, default=0)

    def __init__(self, *args, **kwargs):
        super(ContainerChallengeModel, self).__init__(**kwargs)
        self.value = kwargs.get("initial", 0)
        
        # Handle both old and new port configurations
        if "port" in kwargs:
            self.port = kwargs["port"]
            self.port_range_start = kwargs["port"]
            self.port_range_end = kwargs["port"]
        elif "port_range_start" in kwargs and "port_range_end" in kwargs:
            self.port_range_start = kwargs["port_range_start"]
            self.port_range_end = kwargs["port_range_end"]
            self.port = self.port_range_start  # For backward compatibility

class ContainerInfoModel(db.Model):
    """
    Represents information about a running container instance.
    """
    __tablename__ = "container_info_model"
    container_id = db.Column(db.String(512), primary_key=True)
    challenge_id = db.Column(
        db.Integer, db.ForeignKey("challenges.id", ondelete="CASCADE")
    )
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE")
    )
    team_id = db.Column(
        db.Integer, db.ForeignKey("teams.id", ondelete="CASCADE")
    )
    # Keep old port column for backward compatibility
    port = db.Column(db.Integer, nullable=True)
    ports = db.Column(db.Text, nullable=True)  # JSON: {"internal_port": "external_port", ...}
    timestamp = db.Column(db.Integer)
    expires = db.Column(db.Integer)

    user = db.relationship("Users", foreign_keys=[user_id])
    team = db.relationship("Teams", foreign_keys=[team_id])
    challenge = db.relationship(ContainerChallengeModel,
                              foreign_keys=[challenge_id])

class ContainerSettingsModel(db.Model):
    """
    Represents configuration settings for the containers plugin.
    """
    __tablename__ = "container_settings_model"
    key = db.Column(db.String(512), primary_key=True)
    value = db.Column(db.Text)

    @classmethod
    def apply_default_config(cls, key, value):
        if not cls.query.filter_by(key=key).first():
            db.session.add(cls(key=key, value=value))
