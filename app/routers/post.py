from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy import func
from sqlalchemy.orm import Session
from .. import models, schemas, oauth2
from ..database import get_db

router = APIRouter(
    prefix="/posts",    # Removes the need to have /posts in the decorattors.
    tags=["Posts"]  # updates the /docs with a title for the API endpoints
)

# FastAPI shows the first occurance of a unique HTTP method + "/" URL combination i.e. the order of the functions matters if there are duplicate methods + URLs.
# @router.get("/", response_model=list[schemas.PostResponse])
@router.get("/", response_model=list[schemas.PostOut])
def get_posts(db: Session = Depends(get_db), current_user: int =  Depends(oauth2.get_current_user), limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    # with database as conn:
    #     cur = conn.cursor()
    #     posts = cur.execute("""SELECT * FROM posts """).fetchall()

    # Can put a query parameters in the Postman GET to limit the number of posts returned and skip posts e.g. {{URL}}posts?limit=3&skip=2
    # search is another query parameter to get posts back that contain the search string. %20 means blank space in URL.
    # posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()

    # SQL: select posts.*, COUNT(votes.post_id) as votes from posts LEFT OUTER JOIN votes ON posts.id = votes.post_id groub by posts.id
    posts = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(
            models.Post.title.contains(search)).limit(limit).offset(skip).all()

    return posts

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
# FastAPI checks the data it receives against the Post class. 
# Can therefore access information easier e.g. new_post.title. 
# Also fails when things are sent in a way that doesn't match the Post model.
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int =  Depends(oauth2.get_current_user)):
    # with database as conn:
    #     cur = conn.cursor()
    #     # Doing %s stops a SQL injection attack by sanitising the inputs.
    #     cur.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """, 
    #                 (post.title, post.content, post.published))
    #     new_post = cur.fetchone()
    #     conn.commit()
    new_post = models.Post(owner_id=current_user.id, **post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.get("/{id}", response_model=schemas.PostOut)
def get_post(id: int, db: Session = Depends(get_db), current_user: int =  Depends(oauth2.get_current_user)):
    # with database as conn:
    #     cur = conn.cursor()
    #     # Have to pass a tuple to the %s part of cur.execute so it is (id,)
    #     post = cur.execute("""SELECT * FROM posts WHERE id = %s""", (str(id),)).fetchone()
    # post = db.query(models.Post).filter(models.Post.id == id).first()

    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"post with id: {id} was not found")
    return post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user: int =  Depends(oauth2.get_current_user)):
    # deleting post
    # find the index in the array that has required ID
    # with database as conn:
    #     cur = conn.cursor()
    #     deleted_post = cur.execute("""DELETE FROM posts WHERE id = %s returning *""", (str(id),)).fetchone()
    #     conn.commit()
    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exist")
    
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorised to perform requested action")

    post_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=schemas.PostResponse)
def update_post(id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int =  Depends(oauth2.get_current_user)):
    # with database as conn:
    #     cur = conn.cursor()
    #     updated_post = cur.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""", (post.title, post.content, post.published, str(id))).fetchone()
    #     conn.commit()
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exist")
    
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorised to perform requested action")

    post_query.update(updated_post.model_dump(), synchronize_session=False)
    db.commit()
    return post_query.first()