import logging
import os
import sys
from flask import Flask
from schema.posts import PostSchema
from model.unicode_enum_attribute import UnicodeEnumAttribute
from enums.platform import Platform
from flask_cors import CORS

# Register controllers (blueprints)
from controllers.influencer_metrics_controller import bp as influencer_metrics_bp
from controllers.posts_controller import bp as posts_bp

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

post_schema = PostSchema()
posts_schema = PostSchema(many=True)

# Allow requests from your Next.js frontend
CORS(app, origins=["http://localhost:3000"])

def serialize_post(post):
    data = post_schema.dump(post)
    if 'platform' in data and isinstance(post.platform, Platform):
        data['platform'] = UnicodeEnumAttribute(Platform).serialize(post.platform)
    return data


def serialize_posts(posts):
    return [serialize_post(post) for post in posts]


# Register blueprints moved to controllers
app.register_blueprint(influencer_metrics_bp)
app.register_blueprint(posts_bp)


def handler(event, context):
    # import awsgi lazily so tests can import this module without requiring awsgi to be installed
    try:
        import awsgi
    except Exception:
        # If awsgi isn't available, raise — handler is only used in AWS runtime.
        raise
    return awsgi.response(app, event, context)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
