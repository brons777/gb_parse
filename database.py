from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import models


class Database:
    def __init__(self, db_url):
        engine = create_engine(db_url)
        models.Base.metadata.create_all(bind=engine)
        self.maker = sessionmaker(bind=engine)

    def get_or_create(self, session, model, **data):
        try:
            if data['url']:
                db_data = session.query(model).filter(model.url == data["url"]).first()
                if not db_data:
                    db_data = model(**data)
                return db_data
        except (TypeError, KeyError):
            db_data = model(**data)
            return db_data
        except AttributeError:
            db_data = model(**data)
            return db_data

    def create_post(self, data):
        session = self.maker()
        tags = map(
            lambda tag_data: self.get_or_create(session, models.Tag, **tag_data),
            data['tags']
        )
        author = self.get_or_create(session, models.Author, **data['author'])
        post = self.get_or_create(session, models.Post, **data['data_post'], author=author)
        comment = self.get_or_create(session, models.Comment, **data['comments'], author=author)
        # comment = models.Comment(**data['comments'])
        post.tags.extend(tags)

        session.add(post)
        session.add(comment)

        try:
            session.commit()
        except Exception:
            session.rollback()
        finally:
            session.close()