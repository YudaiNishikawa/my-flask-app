#Unit Test
import unittest
from app import app, db
from app.models import User, Post
from datetime import datetime, timedelta

class UserModelCase(unittest.TestCase):
    def setUp(self):
        # テスト中だけ使う「メモリ上のデータベース」を作成
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        app.config['TESTING']=True
        self.app_context=app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        # テストが終わったら中身を消去
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_follow(self):
        u1 = User(username='john', email='john@example.com')
        u2 = User(username='susan', email='susan@example.com')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        
        # 最初は誰もフォローしていないはず
        self.assertEqual(u1.followed.all(), [])
        
        # フォローのテスト
        u1.follow(u2)
        db.session.commit()
        self.assertTrue(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 1)
        
        # フォロー解除のテスト
        u1.unfollow(u2)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 0)

if __name__ == '__main__':
    unittest.main(verbosity=2)