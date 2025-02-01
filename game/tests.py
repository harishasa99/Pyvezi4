from django.test import TestCase
from game.models import GameLog

class GameLogTestCase(TestCase):
    def test_create_game_log(self):
        log = GameLog.objects.create(log_data="Test log data")
        self.assertEqual(GameLog.objects.count(), 1)
        self.assertEqual(log.log_data, "Test log data")
