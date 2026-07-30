import io
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
        self.assertEqual(stems.get_json(), [{'name': 'drums.wav', 'url': '/stems/drums.wav'}])


if __name__ == '__main__':
    unittest.main()
