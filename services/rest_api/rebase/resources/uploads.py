from atexit import register
import hashlib
from magic import Magic, MAGIC_MIME_TYPE
from os import path

from flask_restful import Resource
from flask_login import login_required, current_user, current_app
from flask import jsonify, request, send_from_directory

from ..common.aws import s3
from ..common.config import S3_BUCKET
from ..common.database import DB
from ..models import Photo
from ..views import user


ALLOWED_MIMETYPES = { 'image/jpeg' }
MAGIC = Magic(flags=MAGIC_MIME_TYPE)
register(MAGIC.close)

uploads = S3_BUCKET + '/uploads/'


def allowed_file_type(filebuffer):
    return MAGIC.id_buffer(filebuffer) in ALLOWED_MIMETYPES


class UploadCollection(Resource):

    url = '/uploads'

    def post(self):
        file_ = request.files['photo']
        # TODO uncomment the following line once Alpine Linux version 3.4.6 (upcoming) has been released.
        # That release has a fix for: https://bugs.alpinelinux.org/issues/5264#change-17546
        # which currently prevents Magic from working.
        # Also, we should add validation client-side to reduce strain on server.
        # Also, investigate leveraging Nginx to do this type of job. (media type checking, file size limitations, etc.)
        #if allowed_file_type(file_.stream.getvalue()):
        filename = uploads+hashlib.sha1(file_.stream.getvalue()).hexdigest() + '.jpeg'
        #TODO save file to S3
        #file_.save(path.join(current_app.config['UPLOAD_FOLDER'], filename))
        photo = Photo.query.filter(Photo.user_id == current_user.id).first()
        if photo:
            photo.filename = filename
        else:
            photo = Photo(filename=filename, user=current_user)
            DB.session.add(photo)
        DB.session.commit()
        response = jsonify(**{'user': user.serializer.dump(current_user).data, 'message': 'Photo Uploaded'})
        response.status_code = 200
        return response


class UploadResource(Resource):

    url = '/uploads/<filename>'

    def get(self, filename):
        return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)


