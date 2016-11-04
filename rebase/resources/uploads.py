from atexit import register
import hashlib
from magic import Magic, MAGIC_MIME_TYPE

from os import path
from flask.ext.restful import Resource
from flask.ext.login import login_required, current_user, current_app
from flask import jsonify, request, send_from_directory

from rebase.views import user
from rebase.models import Photo
from rebase.common.database import DB


ALLOWED_MIMETYPES = { 'image/jpeg' }
MAGIC = Magic(flags=MAGIC_MIME_TYPE)
register(MAGIC.close)


def allowed_file_type(filebuffer):
    return MAGIC.id_buffer(filebuffer) in ALLOWED_MIMETYPES


class UploadCollection(Resource):
    url = '/uploads'

    def post(self):
        file = request.files['photo']
        # TODO uncomment the following line once Alpine Linux version 3.4.6 (upcoming) has been released.
        # That release has a fix for: https://bugs.alpinelinux.org/issues/5264#change-17546
        # which currently prevents Magic from working.
        #if allowed_file_type(file.stream.getvalue()):
        filename = hashlib.sha1(file.stream.getvalue()).hexdigest() + '.jpeg'
        file.save(path.join(current_app.config['UPLOAD_FOLDER'], filename))
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
