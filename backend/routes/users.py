from fastapi import APIRouter,status,HTTPException


from ..dependencies import logger
from ..services.utils import db_dependency, user_dependency
from ..models.users_models import Steaks
from ..models.users_models import Language
from..schemas.steak_schemas import SteakSchemas
from..schemas.language_schemas import LanguageSchema


router=APIRouter(
  prefix="/users",
  tags=["users",]
)


#Технології

@router.get('/get_all_technologies',status_code=status.HTTP_200_OK)
async def get_all_technologies(db: db_dependency, user: user_dependency):
  if not user:
    logger.warning("Користувач не знайдено")
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user')
  technologies = db.query(Steaks).filter_by(user_id=user.get("id")).all()
  if technologies:
    logger.info(f"Знайдено {len(technologies)} технологій для користувача {user.get('email')}")
    return technologies
  else:
    logger.warning("Технологі�� не знайдено")
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Technologies not found')

@router.post('/add_technology',status_code=status.HTTP_201_CREATED)
async def add_technology(steak: SteakSchemas, db: db_dependency , user: user_dependency):
  if not user:
    logger.warning("Користувач не знайдено")
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user')
  existing_technology = db.query(Steaks).filter(
        Steaks.user_id == user.get("id"),
        Steaks.technology == steak.technology
    ).first()

  if existing_technology:
    logger.info(f"Користувач {user.get('email')} вже має технологію {steak.technology}")
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ця технологія вже додана")
  create_technology=Steaks(
    user_id=user.get("id"),
    technology=steak.technology,
  )
  db.add(create_technology)
  db.commit()
  logger.info(f"Технологія {steak.technology} додана для користувача {user.get('email')}")
  return create_technology

@router.delete('/delete_technology',status_code=status.HTTP_204_NO_CONTENT)
async def delete_technology(technology: str, db: db_dependency, user: user_dependency):
  if not user:
    logger.warning("Користувач не знайдено")
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user')
  existing_technology = db.query(Steaks).filter(
        Steaks.user_id == user.get("id"),
        Steaks.technology == technology
    ).first()
  if not existing_technology:
    logger.info(f"Користувач {user.get('email')} не має технологі�� {technology}")
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Технологія не знайдена")
  db.delete(existing_technology)
  db.commit()
  logger.info(f"Технологія {technology} видалена для користувача {user.get('email')}")
  return {"message": "Технологія була успішно видалена"}



#Мови

@router.get('/get_all_languages',status_code=status.HTTP_200_OK)
async def get_all_languages(db: db_dependency, user: user_dependency):
  if not user:
    logger.warning("Користувач не знайдено")
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user')
  languages = db.query(Language).filter_by(user_id=user.get("id")).all()
  if languages:
    logger.info(f"Знайдено {len(languages)} мови для користувача {user.get('email')}")
    return languages
  else:
    logger.warning("Мови не знайдено")
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Languages not found')


@router.post('/add_languages',status_code=status.HTTP_200_OK)
async def read_all_languages(language:LanguageSchema,db: db_dependency,user:user_dependency):
  if not user:
    logger.warning("Користувач не знайдено")
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user')
  existing_languages = db.query(Language).filter(
        Language.user_id == user.get("id"),
        Language.language == language.language
    ).first()

  if existing_languages:
    logger.info(f"Користувач {user.get('email')} вже має мову {language.language}")
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ця мова вже додана")
  create_languages=Language(
    user_id=user.get("id"),
    language=language.language,
  )
  db.add(create_languages)
  db.commit()
  logger.info(f"Мова {language.language} додана для користувача {user.get('email')}")
  return create_languages

@router.delete('/delete_language',status_code=status.HTTP_204_NO_CONTENT)
async def delete_language(language: str, db: db_dependency, user: user_dependency):
  if not user:
    logger.warning("Користувач не знайдено")
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user')
  existing_language = db.query(Language).filter(
        Language.user_id == user.get("id"),
        Language.language == language
    ).first()
  if not existing_language:
    logger.info(f"Користувач {user.get('email')} не має мови {language}")
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Мова не знайдена")
  db.delete(existing_language)
  db.commit()
  logger.info(f"Мова {language} видалена для користувача {user.get('email')}")
  return {"message": "Мова була успішно видалена"}


