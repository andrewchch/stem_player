import io
import json
import tempfile
import unittest
from pathlib import Path

import app as stem_app


class StemAppTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        stem_app.STEMS_DIR = Path(self.temp_dir.name)
        self.client = stem_app.app.test_client()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_lists_no_stems_initially(self):
        response = self.client.get('/api/stems')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [])

    def test_upload_rejects_non_audio_file(self):
        response = self.client.post(
            '/api/upload',
            data={'files': (io.BytesIO(b'data'), 'notes.txt')},
            content_type='multipart/form-data',
        )
        self.assertEqual(response.status_code, 400)

    def test_upload_and_list_audio_file(self):
        upload = self.client.post(
            '/api/upload',
            data={'files': (io.BytesIO(b'RIFF....WAVE'), 'drums.wav')},
            content_type='multipart/form-data',
        )
        self.assertEqual(upload.status_code, 200)
        self.assertIn('drums.wav', upload.get_json()['uploaded'])

        stems = self.client.get('/api/stems')
        self.assertEqual(stems.status_code, 200)
        data = stems.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'drums.wav')
        self.assertEqual(data[0]['url'], '/stems/drums.wav')
        self.assertIn('size', data[0])
        self.assertIn('added', data[0])

    # ---- folder API tests ----

    def test_list_folders_empty(self):
        response = self.client.get('/api/folders')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [])

    def test_create_folder(self):
        response = self.client.post(
            '/api/folders',
            data=json.dumps({'name': 'project1'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['name'], 'project1')
        folders = self.client.get('/api/folders').get_json()
        self.assertIn('project1', folders)

    def test_create_folder_invalid_name(self):
        response = self.client.post(
            '/api/folders',
            data=json.dumps({'name': ''}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)

    def test_upload_to_folder(self):
        # Create folder first
        self.client.post(
            '/api/folders',
            data=json.dumps({'name': 'band'}),
            content_type='application/json',
        )

        upload = self.client.post(
            '/api/upload',
            data={
                'files': (io.BytesIO(b'RIFF....WAVE'), 'guitar.wav'),
                'folder': 'band',
            },
            content_type='multipart/form-data',
        )
        self.assertEqual(upload.status_code, 200)
        self.assertIn('guitar.wav', upload.get_json()['uploaded'])

        stems = self.client.get('/api/stems?folder=band')
        self.assertEqual(stems.status_code, 200)
        data = stems.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'guitar.wav')
        self.assertEqual(data[0]['url'], '/stems/band/guitar.wav')

    def test_upload_to_nonexistent_folder_fails(self):
        response = self.client.post(
            '/api/upload',
            data={
                'files': (io.BytesIO(b'RIFF....WAVE'), 'bass.wav'),
                'folder': 'nope',
            },
            content_type='multipart/form-data',
        )
        self.assertEqual(response.status_code, 404)

    def test_list_stems_for_nonexistent_folder_fails(self):
        response = self.client.get('/api/stems?folder=nope')
        self.assertEqual(response.status_code, 404)

    def test_admin_page_renders(self):
        response = self.client.get('/admin')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Admin', response.data)

    def test_upload_replaces_existing_file(self):
        self.client.post(
            '/api/folders',
            data=json.dumps({'name': 'proj'}),
            content_type='application/json',
        )
        for content in (b'version1', b'version2'):
            self.client.post(
                '/api/upload',
                data={
                    'files': (io.BytesIO(content), 'track.wav'),
                    'folder': 'proj',
                },
                content_type='multipart/form-data',
            )
        stems = self.client.get('/api/stems?folder=proj').get_json()
        self.assertEqual(len(stems), 1)


if __name__ == '__main__':
    unittest.main()
