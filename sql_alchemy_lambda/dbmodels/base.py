from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

DEFAULT_EXCLUDED_ATTRS = ["__mapper__", "_sa_instance_state"]
Base = declarative_base()


class BaseModel(Base):
    """
    Base model class with some common functions used by multiple models
    """

    __abstract__ = True
    _excluded_attributes = None
    _serialize_columns_only = False

    def __init__(self, **kwargs):
        """
        Update 'created' timestamp on object creation, if the model has one
        """
        if hasattr(self, "rec_created_ts"):
            setattr(self, "rec_created_ts", datetime.now())
        super().__init__(**kwargs)

    def __str__(self):
        primary_keys = [pk.name for pk in self.__mapper__.primary_key]
        primary_key_values = ",".join([str(getattr(self, pk)) for pk in primary_keys])
        return "{}(id:{})".format(self.__class__.__name__, primary_key_values)

    def update_from_params(self, params):
        """
        Update values based on provided key-value pairs that match model attributes.

        TODO: This should be replaced by validating request params against a serialization schema.
        """
        for k, v in params.items():
            if hasattr(self, k):
                setattr(self, k, v)
        self.update_timestamp()

    def update_timestamp(self):
        """
        Update 'last updated' timestamp, if the model has one
        """
        if hasattr(self, "rec_updated_ts"):
            setattr(self, "rec_updated_ts", datetime.now())

    @property
    def excluded_attributes(self):
        """
        Get a set of attributes to be excludedc from serialization
        """
        synonyms = self.__mapper__.synonyms.keys()
        return set(DEFAULT_EXCLUDED_ATTRS + synonyms + (self._excluded_attributes or []))

    def as_dict(self):
        """
        Return a dictionary of attributes and values, minus any explicitly excluded ones.

        An intermediate replacement for previously hardcoded as_dict() to_dict functions, but should
        be replaced with generated serialization schemas.

        If ``_serialize_columns_only`` is True, return only real columns. Otherwise return all
        model properties, including real columns and derived attributes.
        """
        if self._serialize_columns_only:
            attributes = [col.name for col in self.__mapper__.columns]
        else:
            attributes = self.__mapper__.all_orm_descriptors.keys()
        return {k: getattr(self, k, None) for k in set(attributes) - self.excluded_attributes}
